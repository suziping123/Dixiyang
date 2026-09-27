package com.dixiyang.server.Entity.dto;

import lombok.Data;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Data
public class PasswordDTO {
    private String oldPassword;
    private String newPassword;
}
