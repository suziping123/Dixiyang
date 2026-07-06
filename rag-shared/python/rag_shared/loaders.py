"""各类数据源的加载与切分器"""
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Generator
from dataclasses import dataclass, asdict

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import RAGConfig


@dataclass
class DocumentChunk:
    """文档分块"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
            "source": self.source
        }


class BaseLoader:
    """基础加载器"""

    def __init__(self, config: RAGConfig):
        self.config = config

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        raise NotImplementedError


class MarkdownLoader(BaseLoader):
    """Markdown 文件加载器（按标题层级语义切分）"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        text = file_path.read_text(encoding='utf-8')
        filename = file_path.stem
        book_title, author = self._parse_filename(filename)
        category = self.config.raw.get('book_categories', {}).get(book_title, "其他")
        sections = self._split_by_headers(text)

        chunk_index = 0
        for section in sections:
            sub_chunks = self._split_text(section['content'])
            for sub_chunk in sub_chunks:
                if len(sub_chunk.strip()) < self.config.raw.get('preprocessing', {}).get('min_chunk_length', 50):
                    continue

                metadata = {
                    "source": "book",
                    "book_title": book_title,
                    "author": author,
                    "category": category,
                    "chapter": section.get('h1', ''),
                    "section": section.get('h2', ''),
                    "chunk_id": f"{book_title}_{chunk_index}",
                    "file_path": str(file_path)
                }

                yield DocumentChunk(
                    content=sub_chunk.strip(),
                    metadata=metadata,
                    chunk_id=metadata["chunk_id"],
                    source="book"
                )
                chunk_index += 1

    def _parse_filename(self, filename: str) -> tuple:
        match = re.match(r'^(.+?)\s*\((.+?)\)$', filename)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return filename, "未知"

    def _split_by_headers(self, text: str) -> List[Dict[str, str]]:
        lines = text.split('\n')
        sections = []
        current_h1 = ""
        current_h2 = ""
        current_content = []

        for line in lines:
            h1_match = re.match(r'^#\s+(.+)$', line)
            h2_match = re.match(r'^##\s+(.+)$', line)

            if h1_match:
                if current_content:
                    sections.append({
                        'h1': current_h1, 'h2': current_h2,
                        'content': '\n'.join(current_content)
                    })
                current_h1 = h1_match.group(1)
                current_h2 = ""
                current_content = [line]
            elif h2_match:
                if current_content:
                    sections.append({
                        'h1': current_h1, 'h2': current_h2,
                        'content': '\n'.join(current_content)
                    })
                current_h2 = h2_match.group(1)
                current_content = [line]
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                'h1': current_h1, 'h2': current_h2,
                'content': '\n'.join(current_content)
            })
        return sections

    def _split_text(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
            keep_separator=True,
        )
        return splitter.split_text(text)


class CSVLoader(BaseLoader):
    """CSV 文件加载器"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        import pandas as pd

        df = pd.read_csv(file_path)
        filename = file_path.stem
        dataset_types = self.config.raw.get('dataset_types', {})

        for idx, row in df.iterrows():
            dtype = self._detect_dataset_type(filename, dataset_types)
            type_config = dataset_types.get(dtype, {})

            if dtype == 'cars':
                template = type_config.get('template', "{leixing} {nianfen} {licheng} {didian} {shoujia} {yuanjia}")
                content = template.format(**row.to_dict())
                metadata = {
                    "source": "cars",
                    "brand": row.get('leixing', '').split()[0] if row.get('leixing') else '',
                    "model": row.get('leixing', ''),
                    "year": str(row.get('nianfen', '')),
                    "mileage": str(row.get('licheng', '')),
                    "city": str(row.get('didian', '')),
                    "price": str(row.get('shoujia', '')),
                    "original_price": str(row.get('yuanjia', '')),
                    "chunk_id": f"cars_{idx}",
                    "file_path": str(file_path)
                }
            elif dtype == 'law':
                content = row.get('text', '')
                article_match = re.search(r'《.+?》第.+?条', content)
                article_num = article_match.group() if article_match else ''
                metadata = {
                    "source": "law",
                    "law_name": self._extract_law_name(content),
                    "article_num": article_num,
                    "chunk_id": f"law_{idx}",
                    "file_path": str(file_path)
                }
            else:
                content = row.to_json(force_ascii=False)
                metadata = {
                    "source": "csv",
                    "file": filename,
                    "row": idx,
                    "chunk_id": f"csv_{filename}_{idx}",
                    "file_path": str(file_path)
                }

            if content.strip():
                yield DocumentChunk(
                    content=content.strip(),
                    metadata=metadata,
                    chunk_id=metadata["chunk_id"],
                    source=dtype or "csv"
                )

    def _detect_dataset_type(self, filename: str, dataset_types: Dict) -> str:
        for dtype, config in dataset_types.items():
            pattern = config.get('file_pattern', '')
            if pattern and pattern.replace('*', '') in filename:
                return dtype
        return 'unknown'

    def _extract_law_name(self, text: str) -> str:
        match = re.search(r'《(.+?)》', text)
        return match.group(1) if match else "未知法律"


class TextLoader(BaseLoader):
    """纯文本加载器"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        text = file_path.read_text(encoding='utf-8')
        filename = file_path.stem
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        dataset_types = self.config.raw.get('dataset_types', {})
        dtype = self._detect_dataset_type(filename, dataset_types)

        for idx, para in enumerate(paragraphs):
            if len(para) < 20:
                continue
            metadata = {
                "source": dtype or "text",
                "company": filename,
                "section": f"段落_{idx}",
                "chunk_id": f"{dtype}_{filename}_{idx}",
                "file_path": str(file_path)
            }
            yield DocumentChunk(
                content=para,
                metadata=metadata,
                chunk_id=metadata["chunk_id"],
                source=dtype or "text"
            )

    def _detect_dataset_type(self, filename: str, dataset_types: Dict) -> str:
        for dtype, config in dataset_types.items():
            pattern = config.get('file_pattern', '')
            if pattern and pattern.replace('*', '') in filename:
                return dtype
        return 'unknown'


class JSONLoader(BaseLoader):
    """JSON 文件加载器（QA 对）"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filename = file_path.stem
        dataset_types = self.config.raw.get('dataset_types', {})
        dtype = 'qa'

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            instruction = item.get('instruction', '')
            input_text = item.get('input', '')
            output = item.get('output', '')
            content = f"指令：{instruction}\n问题：{input_text}\n回答：{output}"
            category = self._classify_qa(instruction, input_text)

            metadata = {
                "source": "qa",
                "instruction": instruction,
                "input": input_text,
                "output": output,
                "category": category,
                "chunk_id": f"qa_{idx}",
                "file_path": str(file_path)
            }

            yield DocumentChunk(
                content=content,
                metadata=metadata,
                chunk_id=metadata["chunk_id"],
                source="qa"
            )

    def _classify_qa(self, instruction: str, input_text: str) -> str:
        text = (instruction + input_text).lower()
        keywords = {
            '中医': ['中医', '辨证', '方剂', '舌苔', '脉象', '气血', '阴阳'],
            '西医内科': ['心衰', '肺炎', '高血压', '糖尿病', '冠心病', '脑梗'],
            '外科': ['手术', '切除', '阑尾', '疝气', '胆结石'],
            '妇产科': ['妊娠', '产前', '胎儿', '孕妇', '分娩'],
            '儿科': ['新生儿', '婴儿', '小儿', '发热', '惊厥'],
            '药理': ['用药', '药物', '剂量', '副作用', '相互作用'],
            '医学统计': ['计算', '概率', '统计', '置信区间', 'P值'],
        }
        for cat, kws in keywords.items():
            if any(kw in text for kw in kws):
                return cat
        return '其他'
