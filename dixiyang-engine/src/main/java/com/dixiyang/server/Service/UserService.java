package com.dixiyang.server.Service;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.VO.UserVO;
import com.dixiyang.server.Entity.dto.PasswordDTO;
import com.dixiyang.server.Entity.dto.UserUpdateDTO;
import com.dixiyang.server.Entity.dto.BackgroundConfigDTO;

/**
 * @author SuZiPing
 * @version 1.0
 */
public interface UserService {
    Result<UserVO> updateUser(UserUpdateDTO request);
    Result<Void> changePassword(PasswordDTO dto);
    Result getCurrentUserInfo();

    /**
     * 获取用户背景和颜色配置
     * @return 用户保存的配置，如果没有则返回 null
     */
    Result<BackgroundConfigDTO> getBackgroundConfig();

    /**
     * 保存用户背景和颜色配置
     * 包括背景预设和自定义字体颜色
     * @param config 背景配置对象（包含 fontColors 字段）
     * @return 保存结果
     */
    Result<Void> saveBackgroundConfig(BackgroundConfigDTO config);

}
