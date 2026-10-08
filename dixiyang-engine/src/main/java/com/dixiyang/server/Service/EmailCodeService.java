package com.dixiyang.server.Service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.EmailVerificationCode;
import com.dixiyang.server.Mapper.EmailVerificationCodeMapper;
import com.dixiyang.server.Utils.DotEnv;
import jakarta.mail.internet.MimeMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 邮箱验证码服务（与 DixyangFast email_service/auth_service 行为对齐）
 * 时间一律用 UTC 字面值写入，保证与 Python 端共表可比
 */
@Service
public class EmailCodeService {
    private static final Logger log = LoggerFactory.getLogger(EmailCodeService.class);
    private static final int CODE_EXPIRE_MINUTES = 5;
    private static final int RATE_LIMIT_SECONDS = 60;

    private final EmailVerificationCodeMapper mapper;
    private final JavaMailSender mailSender;

    @Value("${spring.mail.username:}")
    private String fromAddress;
    @Value("${spring.mail.host:}")
    private String mailHost;

    @Autowired
    public EmailCodeService(EmailVerificationCodeMapper mapper, JavaMailSender mailSender) {
        this.mapper = mapper;
        this.mailSender = mailSender;
    }

    /**
     * 环境变量缺失时从项目根 .env 兜底（与 Python config.load_dotenv 对齐）
     */
    @PostConstruct
    void initMailCredential() {
        if (fromAddress == null || fromAddress.isBlank()) {
            fromAddress = DotEnv.get("SMTP_USERNAME", "MAIL_USERNAME");
        }
        String password = DotEnv.get("SMTP_PASSWORD", "MAIL_PASSWORD");
        if (mailSender instanceof JavaMailSenderImpl impl) {
            if (impl.getUsername() == null || impl.getUsername().isBlank()) {
                impl.setUsername(fromAddress == null ? "" : fromAddress);
            }
            if ((impl.getPassword() == null || impl.getPassword().isBlank()) && password != null) {
                impl.setPassword(password);
            }
        }
    }

    /**
     * 发送验证码（60秒限流 + 5分钟有效 + 一次性）
     */
    public Result<Void> sendCode(String email, String purpose) {
        if (email == null || email.isBlank()) {
            return Result.error("邮箱不能为空");
        }
        if (!"LOGIN".equals(purpose) && !"REGISTER".equals(purpose) && !"CHG_EMAIL".equals(purpose)) {
            return Result.error("用途参数无效");
        }
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        EmailVerificationCode last = selectLatest(email, purpose);
        if (last != null && last.getCreatedAt() != null
                && last.getCreatedAt().isAfter(now.minusSeconds(RATE_LIMIT_SECONDS))) {
            long wait = RATE_LIMIT_SECONDS - Duration.between(last.getCreatedAt(), now).getSeconds();
            return Result.error("请" + Math.max(wait, 1) + "秒后重试");
        }

        String code = String.format("%06d", ThreadLocalRandom.current().nextInt(1_000_000));
        // 先发信后落库：发送失败不留记录，避免限流把用户锁死
        if (!sendMail(email, code)) {
            return Result.error("验证码邮件发送失败，请稍后重试");
        }

        if (last == null) {
            EmailVerificationCode record = new EmailVerificationCode();
            record.setEmail(email);
            record.setCode(code);
            record.setPurpose(purpose);
            record.setExpireTime(now.plusMinutes(CODE_EXPIRE_MINUTES));
            record.setUsed(false);
            record.setCreatedAt(now);
            mapper.insert(record);
        } else {
            last.setCode(code);
            last.setExpireTime(now.plusMinutes(CODE_EXPIRE_MINUTES));
            last.setUsed(false);
            last.setCreatedAt(now);
            mapper.updateById(last);
        }
        log.info("验证码邮件已发送: to={}", email);
        return Result.success("验证码已发送", null);
    }

    /**
     * 校验并消费验证码（一次性：校验通过即置 used）
     */
    public boolean verifyCode(String email, String purpose, String code) {
        if (email == null || code == null) {
            return false;
        }
        EmailVerificationCode record = selectLatest(email, purpose);
        if (record == null || Boolean.TRUE.equals(record.getUsed())) {
            return false;
        }
        if (record.getExpireTime() == null
                || !record.getExpireTime().isAfter(LocalDateTime.now(ZoneOffset.UTC))) {
            return false;
        }
        if (!record.getCode().equals(code.trim())) {
            return false;
        }
        record.setUsed(true);
        mapper.updateById(record);
        return true;
    }

    private EmailVerificationCode selectLatest(String email, String purpose) {
        LambdaQueryWrapper<EmailVerificationCode> qw = new LambdaQueryWrapper<>();
        qw.eq(EmailVerificationCode::getEmail, email)
                .eq(EmailVerificationCode::getPurpose, purpose)
                .orderByDesc(EmailVerificationCode::getId)
                .last("LIMIT 1");
        return mapper.selectOne(qw);
    }

    private boolean sendMail(String to, String code) {
        if (mailHost == null || mailHost.isBlank() || fromAddress == null || fromAddress.isBlank()) {
            log.error("SMTP 配置缺失: spring.mail.host={}, spring.mail.username 已设置={}",
                    mailHost, fromAddress != null && !fromAddress.isBlank());
            return false;
        }
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setFrom(fromAddress);
            helper.setTo(to);
            helper.setSubject("【DIXIYANG】邮箱验证码");
            helper.setText(buildHtml(code), true);
            mailSender.send(message);
            return true;
        } catch (Exception e) {
            log.error("发送验证码邮件失败: to={}, error={}", to, e.getMessage());
            return false;
        }
    }

    private String buildHtml(String code) {
        return """
                <div style="max-width:400px;margin:0 auto;padding:20px;font-family:Arial,sans-serif;">
                  <h2 style="text-align:center;color:#6366f1;">DIXIYANG ENGINE</h2>
                  <p>您好，您的邮箱验证码为：</p>
                  <div style="text-align:center;margin:20px 0;">
                    <span style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#333;">%s</span>
                  </div>
                  <p style="color:#999;font-size:13px;">验证码 5 分钟内有效，请勿泄露给他人。</p>
                  <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
                  <p style="color:#bbb;font-size:12px;">如非本人操作，请忽略此邮件。</p>
                </div>
                """.formatted(code);
    }
}
