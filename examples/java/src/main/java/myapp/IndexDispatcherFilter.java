/*
 * Copyright 2016 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package myapp;

import com.google.common.base.Charsets;
import com.google.common.base.Strings;
import com.google.common.io.CharStreams;
import com.google.common.io.Closeables;
import org.json.JSONObject;

import javax.servlet.*;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

public class IndexDispatcherFilter implements Filter {

    private String resourcesToPush;

    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException,
            ServletException {
        String nopush = request.getParameter("nopush");
        if (!Strings.isNullOrEmpty(resourcesToPush) && null == nopush) {
            HttpServletResponse httpResponse = (HttpServletResponse) response;
            httpResponse.addHeader("Link", resourcesToPush);
        }
        RequestDispatcher rd = request.getRequestDispatcher("/index.html");
        rd.forward(request, response);
    }

    public void init(FilterConfig filterConfig) throws ServletException {
        InputStream is = filterConfig.getServletContext().getResourceAsStream("/push_manifest.json");
        try {
            String rawJson = CharStreams.toString(new InputStreamReader(is, Charsets.UTF_8));
            JSONObject pushManifest = new JSONObject(rawJson);
            StringBuilder linkValue = new StringBuilder();
            for(String asset: pushManifest.keySet()) {
                String assetUrl = asset;
                String type = pushManifest.getJSONObject(assetUrl).getString("type");
                linkValue.append("<");
                linkValue.append(assetUrl);
                linkValue.append(">; rel=preload; as=");
                linkValue.append(type);
                linkValue.append(",");
            }
            resourcesToPush = linkValue.toString();
        } catch (IOException e) {
            throw new ServletException(e);
        } finally {
            Closeables.closeQuietly(is);
        }
    }

    public void destroy() {  }

}