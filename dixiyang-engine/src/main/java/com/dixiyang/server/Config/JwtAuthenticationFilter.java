package com.dixiyang.server.Config;

import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Mapper.AppUserMapper;
import com.dixiyang.server.Utils.JwtUtils;
import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private final JwtUtils jwtutils;
    private final AppUserMapper appUserMapper;
    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);
    @Autowired
    public JwtAuthenticationFilter(JwtUtils jwtutils, AppUserMapper appUserMapper) {
        this.jwtutils = jwtutils;
        this.appUserMapper = appUserMapper;
    }
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
    throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);

            try {
                Claims claims = jwtutils.parseClaims(token);
                String userId = claims.getSubject();
                String sid = claims.get("sid", String.class);
                // 单点登录：token 带会话号(sid)时才比对；旧版 token 无 sid，兼容放行至自然过期
                if (sid != null) {
                    AppUser user = appUserMapper.selectById(Long.parseLong(userId));
                    if (user == null || !sid.equals(user.getSessionId())) {
                        write401(response, "账号已在其他设备登录");
                        return;
                    }
                }
                //构建认证对象（核心）
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(userId, null, Collections.emptyList()
                        );
                // 存入上下文后面可以直接拿
                SecurityContextHolder.getContext().setAuthentication(authentication);
                request.setAttribute("userId", Long.parseLong(userId));
            } catch (RuntimeException e) {
                log.warn("JWT 解析失败: {}", e.getMessage());
                write401(response, "Token已过期或无效");
                return;
            } catch (Exception e) {
                log.error("JWT 解析异常", e);
                write401(response, "Token无效");
                return;
            }
        }
        filterChain.doFilter(request, response);
    }

    private void write401(HttpServletResponse response, String msg) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":401,\"msg\":\"" + msg + "\",\"data\":null}");
    }
}
