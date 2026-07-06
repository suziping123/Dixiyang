package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Service.EmailService;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class EmailServiceImpl implements EmailService {

    @Autowired
    private JavaMailSender mailSender;

    @Override
    @Async
    public void sendVerificationCode(String to, String code) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom("suziping123@outlook.com");
            helper.setTo(to);
            helper.setSubject("【DIXIYANG】邮箱验证码");
            helper.setText(buildEmailBody(code), true);

            mailSender.send(message);
            log.info("验证码邮件已发送: to={}", to);
        } catch (MessagingException e) {
            log.error("发送验证码邮件失败: to={}", to, e);
        }
    }

    private String buildEmailBody(String code) {
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
