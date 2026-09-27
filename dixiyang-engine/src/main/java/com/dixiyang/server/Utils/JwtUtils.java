package com.dixiyang.server.Utils;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

@Component
public class JwtUtils {
    // 固定密钥（必须32个字符以上，HS256要求），重启服务也不会变，Token才有效
    private static final String SECRET_STRING = "dixiyang-secret-key-1234567890abcdef12345678";
    private static final SecretKey KEY = Keys.hmacShaKeyFor(SECRET_STRING.getBytes());

    private static final long EXPIRATION_TIME = 7*24*60*60*1000;//7天过期

    /**
     * 根据用户ID生成Token（ID必须是数字，比如"1"，不能是"admin"）
     */
    public String generateToken(String userId){
        // 校验用户ID是否为数字（避免前端传非数字ID）
        if (userId == null || !userId.matches("\\d+")) {
            throw new IllegalArgumentException("用户ID必须是数字格式");
        }
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + EXPIRATION_TIME);

        return Jwts.builder()
                .setSubject(userId)//存用户ID（数字字符串，比如"1"）
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(KEY, SignatureAlgorithm.HS256)//显式指定算法
                .compact();
    }

    /**
     * 解析Token获取用户ID（添加异常处理，避免直接抛错）
     */
    public String getUserIdFromToken(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(KEY)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            return claims.getSubject();
        } catch (SignatureException e) {
            throw new RuntimeException("Token签名验证失败（密钥错误/Token篡改）");
        } catch (ExpiredJwtException e) {
            throw new RuntimeException("Token已过期");
        } catch (MalformedJwtException e) {
            throw new RuntimeException("Token格式错误");
        } catch (Exception e) {
            throw new RuntimeException("Token解析失败：" + e.getMessage());
        }
    }
}