# CORS Configuration for Medical AI Widget

## 🌐 What is CORS?

Cross-Origin Resource Sharing (CORS) is a security feature that controls which websites can access your API. When someone embeds your widget on their website, their domain must be allowed in your CORS configuration.

## 🚫 What happens without proper CORS?

If a domain isn't allowed:
- ❌ Widget shows "I'm having trouble connecting right now"
- ❌ Browser console shows CORS error
- ❌ API calls are blocked by the browser

## ⚙️ Configuration Options

### Option 1: Allow All Origins (Public Widget)
```bash
# Set environment variable on Render/deployment platform
ALLOWED_ORIGINS=*
```
- ✅ Works on any website
- ⚠️ Less secure (allows any domain)
- 👍 Best for public widgets

### Option 2: Specific Domains
```bash
# Allow specific domains only
ALLOWED_ORIGINS=https://example.com,https://mydomain.com,https://*.vercel.app
```
- ✅ More secure
- ⚠️ Must add each customer domain
- 👍 Best for enterprise/controlled deployments

### Option 3: Mixed Approach
```bash
# Allow your domains + wildcard subdomains
ALLOWED_ORIGINS=https://*.yourcompany.com,https://localhost:3000,*
```

## 🔧 How to Update CORS

### For Render Deployment:
1. Go to Render Dashboard
2. Select your backend service
3. Go to "Environment" tab
4. Add environment variable:
   - Key: `ALLOWED_ORIGINS`
   - Value: `*` (for all origins) or `https://domain1.com,https://domain2.com`
5. Redeploy the service

### For Local Development:
Create `.env` file in backend folder:
```bash
ALLOWED_ORIGINS=*
```

## 🧪 Testing CORS

### Test if an origin is allowed:
```bash
curl -X POST https://your-backend.onrender.com/api/cors/test \
  -H "Content-Type: application/json" \
  -d '{"origin": "https://example.com"}'
```

### Check current allowed origins:
```bash
curl https://your-backend.onrender.com/api/cors/origins
```

## 📋 Widget Deployment Checklist

Before giving widget to customers:

1. ✅ Set CORS policy (`*` for public widget)
2. ✅ Test widget on different domains
3. ✅ Update environment variables on hosting platform
4. ✅ Verify API endpoints are accessible
5. ✅ Test with customer's actual domain

## 🚀 Recommended Setup for Production

For a **public widget** (anyone can embed):
```bash
ALLOWED_ORIGINS=*
```

For **enterprise/controlled** deployment:
```bash
ALLOWED_ORIGINS=https://client1.com,https://client2.com,https://*.trusted-partner.com
```

## 🔍 Troubleshooting

**Widget not working on customer site?**
1. Check browser console for CORS errors
2. Test the origin using `/api/cors/test` endpoint
3. Add customer's domain to ALLOWED_ORIGINS
4. Redeploy backend service

**Still having issues?**
- Verify the customer is using HTTPS (not HTTP)
- Check for typos in domain names
- Ensure subdomain wildcards are properly formatted
- Test with a simple curl command first
