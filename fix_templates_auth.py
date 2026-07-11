from pathlib import Path
import re

root = Path('c:/Users/THINKPAD/Downloads/GLIDE-ERP-main/GLIDE-ERP-main')
fixed_files = []
total_files = 0

for path in root.joinpath('templates').rglob('*.html'):
    total_files += 1
    text = path.read_text(encoding='utf-8')
    original = text
    
    # 1. Replace token storage/retrieval
    text = text.replace("localStorage.getItem('access_token')", "JSON.parse(localStorage.getItem('user') || '{}')")
    text = text.replace('localStorage.getItem("access_token")', 'JSON.parse(localStorage.getItem("user") || "{}")')
    text = text.replace("localStorage.setItem('access_token',", "// REMOVED: localStorage.setItem('access_token',")
    text = text.replace('localStorage.setItem("access_token",', '// REMOVED: localStorage.setItem("access_token",')
    text = text.replace("localStorage.removeItem('access_token')", "// REMOVED: localStorage.removeItem('access_token')")
    text = text.replace('localStorage.removeItem("access_token")', '// REMOVED: localStorage.removeItem("access_token")')
    
    # 2. Replace variable declarations
    text = re.sub(r"(?<![\w.])(let|const|var)\s+token\s*=", "const user =", text)
    text = re.sub(r"(?<![\w.])(let|const|var)\s+accessToken\s*=", "const user =", text)
    
    # 3. Fix token checks
    text = re.sub(r"\bif\s*\(\s*!\s*token\s*\)", "if (!user.id)", text)
    text = re.sub(r"\bif\s*\(\s*token\s*\)", "if (user.id)", text)
    text = text.replace("if (!token) {", "if (!user.id) {")
    text = text.replace("if (token) {", "if (user.id) {")
    text = text.replace("if (token)", "if (user.id)")
    text = text.replace("if (!token)", "if (!user.id)")
    
    # 4. Remove Authorization headers (multiple patterns)
    auth_patterns = [
        r"'Authorization':\s*'Bearer\s*'\s*\+\s*\w+",
        r'"Authorization":\s*"Bearer\s*"\s*\+\s*\w+',
        r"'Authorization':\s*'Bearer\s*'\s*\+\s*user",
        r'"Authorization":\s*"Bearer\s*"\s*\+\s*user',
        r"'Authorization':\s*`Bearer\s*\$\{[^}]*\}`",
        r'"Authorization":\s*`Bearer\s*\$\{[^}]*\}`',
    ]
    for pattern in auth_patterns:
        text = re.sub(pattern, "", text)
    
    # 5. Remove headers blocks that contain Authorization
    text = re.sub(r"headers:\s*\{[^}]*'Authorization':\s*'Bearer\s*'\s*\+\s*\w+[^}]*\}", "", text, flags=re.DOTALL)
    text = re.sub(r"headers:\s*\{[^}]*\"Authorization\":\s*\"Bearer\s*\"\s*\+\s*\w+[^}]*\}", "", text, flags=re.DOTALL)
    
    # 6. Clean up empty headers
    text = re.sub(r"headers:\s*\{\s*,\s*", "headers: {", text)
    text = re.sub(r"headers:\s*\{\s*\}", "", text)
    
    # 7. Fix redirect logic
    text = text.replace("window.location.href = '/login/';", "window.location.href = '/login/'; // Redirect to login")
    text = text.replace("if (!user.id) {", "if (!user || !user.id) {")
    
    # 8. Handle base.html specifically
    if path.name == 'base.html':
        # Remove token functions
        text = re.sub(r"function\s+getAuthToken\s*\(\)\s*\{[^}]*\}", "", text, flags=re.DOTALL)
        text = re.sub(r"function\s+isAuthenticated\s*\(\)\s*\{[^}]*\}", "function isAuthenticated() {\n    const user = getCurrentUser();\n    return !!(user && user.id);\n}", text, flags=re.DOTALL)
        text = re.sub(r"function\s+getCurrentUser\s*\(\)\s*\{[^}]*\}", "function getCurrentUser() {\n    try {\n        return JSON.parse(localStorage.getItem('user') || '{}');\n    } catch {\n        return null;\n    }\n}", text, flags=re.DOTALL)
        
        # Remove token cleanup
        text = text.replace("localStorage.removeItem('access_token');", "")
        text = text.replace('localStorage.removeItem("access_token");', "")
        text = text.replace("localStorage.removeItem('refresh_token');", "")
        text = text.replace('localStorage.removeItem("refresh_token");', "")
        text = text.replace("localStorage.setItem('access_token', data.access);", "")
        text = text.replace('localStorage.setItem("access_token", data.access);', "")
        
        # Replace token checks in fetch
        text = text.replace("const token = getAuthToken();", "const user = getCurrentUser();")
        text = re.sub(r"headers:\s*\{\s*'Authorization':\s*'Bearer\s*'\s*\+\s*token\s*,?\s*\}\s*,?", "", text, flags=re.DOTALL)
        text = re.sub(r"headers:\s*\{\s*\"Authorization\":\s*\"Bearer\s*\"\s*\+\s*token\s*,?\s*\}\s*,?", "", text, flags=re.DOTALL)
    
    # 9. Fix fetch URLs that might have token parameters
    text = re.sub(r"\?token=[^&\s]*", "", text)
    text = re.sub(r"&token=[^&\s]*", "", text)
    
    # 10. If text changed, save it
    if text != original:
        path.write_text(text, encoding='utf-8')
        fixed_files.append(str(path.relative_to(root)))
        print(f"✅ Fixed: {path.relative_to(root)}")

print(f"\n📊 Summary:")
print(f"   Total templates found: {total_files}")
print(f"   Files fixed: {len(fixed_files)}")
if fixed_files:
    print(f"   Modified files:")
    for f in fixed_files:
        print(f"     - {f}")
else:
    print("   No files needed fixing!")