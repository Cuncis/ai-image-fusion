# 🚀 Deploy AI Image Fusion Studio to Vercel

Deploy your image fusion tool to Vercel and make it accessible to everyone!

## 📋 Prerequisites

1. **GitHub account** (free) - [Sign up here](https://github.com/join)
2. **Vercel account** (free) - [Sign up here](https://vercel.com/signup)
3. **Gemini API Key** - [Get it free here](https://makersuite.google.com/app/apikey)

## 🎯 Quick Deploy (5 Minutes!)

### Step 1: Upload to GitHub

1. **Create a new repository on GitHub:**
   - Go to [github.com/new](https://github.com/new)
   - Name it: `ai-image-fusion`
   - Keep it Public
   - Click "Create repository"

2. **Upload your files:**
   
   **Option A - Using GitHub Web (Easiest):**
   - Click "uploading an existing file"
   - Drag and drop ALL files from the `vercel-app` folder
   - Click "Commit changes"

   **Option B - Using Git Command Line:**
   ```bash
   cd vercel-app
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-image-fusion.git
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign in

2. **Click "Add New Project"**

3. **Import your GitHub repository:**
   - Click "Import" next to your `ai-image-fusion` repo
   - Vercel will automatically detect the configuration

4. **Click "Deploy"**
   - Wait 2-3 minutes for deployment
   - Done! 🎉

5. **Get your URL:**
   - You'll get a URL like: `https://ai-image-fusion-xxx.vercel.app`
   - Copy this URL!

### Step 3: Test It!

1. Visit your Vercel URL
2. Enter your Gemini API key
3. Upload two images
4. Click "Merge Images with AI"
5. Download your result!

## 🔗 Add to WordPress

Now that your app is on Vercel, add it to WordPress:

### Method 1: iFrame (Easiest)

Add this to any WordPress page:

```html
<iframe 
    src="https://your-app-name.vercel.app" 
    width="100%" 
    height="1400px" 
    frameborder="0"
    style="border: none; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
</iframe>
```

### Method 2: WordPress Plugin

Update the plugin to point to your Vercel URL:

1. Edit `ai-image-fusion-studio.php`
2. Find the line: `$flask_url = get_option('aifs_flask_url', '...');`
3. Change the default to your Vercel URL:
   ```php
   $flask_url = get_option('aifs_flask_url', 'https://your-app.vercel.app/api/merge');
   ```
4. Repackage and upload the plugin

## ⚙️ Project Structure

```
vercel-app/
├── api/
│   └── merge.py           # Serverless API endpoint
├── public/
│   ├── index.html         # Frontend HTML
│   ├── css/
│   │   └── style.css      # Styles
│   └── js/
│       └── script.js      # JavaScript
├── requirements.txt       # Python dependencies
└── vercel.json           # Vercel configuration
```

## 🎨 Customization

### Change Colors

Edit `public/css/style.css`:

```css
:root {
    --primary: #FF6B35;      /* Your color here */
    --secondary: #4ECDC4;    /* Your color here */
}
```

Commit and push changes - Vercel auto-deploys!

### Change Text

Edit `public/index.html` and change any text you want.

### Add Your Logo

1. Add logo file to `public/images/`
2. Edit HTML to include your logo
3. Push changes

## 🔒 Security Best Practices

### 1. Environment Variables (Recommended)

Instead of users entering API keys, you can set ONE key for everyone:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your API key
3. Update `api/merge.py`:

```python
# At the top of merge_images() function:
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    api_key = data.get('api_key')
```

4. Redeploy

### 2. Rate Limiting

To prevent abuse, add to `api/merge.py`:

```python
# At the top
from functools import wraps
import time

request_counts = {}

def rate_limit(max_per_minute=10):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            # Clean old entries
            request_counts[ip] = [t for t in request_counts.get(ip, []) if now - t < 60]
            
            if len(request_counts.get(ip, [])) >= max_per_minute:
                return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
            
            request_counts.setdefault(ip, []).append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Add to merge_images:
@app.route('/api/merge', methods=['POST'])
@rate_limit(max_per_minute=5)  # 5 requests per minute
def merge_images():
    # ...
```

### 3. File Size Limits

Already handled in the code, but you can adjust:

```python
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Check size before processing
if len(person_data) > MAX_FILE_SIZE or len(product_data) > MAX_FILE_SIZE:
    return jsonify({'error': 'File too large. Max 5MB'}), 400
```

## 📊 Monitoring

### View Logs

1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on latest deployment
3. Click "Functions" tab
4. See logs and errors

### Analytics

Vercel provides:
- Page views
- API calls
- Error rates
- Performance metrics

Check: Dashboard → Your Project → Analytics

## 💰 Pricing

### Free Tier Includes:
- ✅ 100 GB bandwidth/month
- ✅ Unlimited requests
- ✅ Automatic SSL
- ✅ Auto-scaling
- ✅ Global CDN

**Note:** Gemini API has separate limits. Free tier includes generous usage.

### If You Need More:
- Pro Plan: $20/month
- More bandwidth and features

## 🔄 Updating Your App

### Automatic Updates:

1. Make changes to your files locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Update design"
   git push
   ```
3. Vercel automatically detects and deploys!
4. Check deployment status in Vercel dashboard

### Manual Deploy:

1. Go to Vercel Dashboard
2. Click "Deployments"
3. Click "Redeploy"

## 🐛 Troubleshooting

### "API Error" or "Merge Failed"

**Check:**
1. Gemini API key is valid
2. Images aren't too large (keep under 5MB)
3. Check Vercel logs for errors

**Solution:**
```bash
# View logs
vercel logs your-project-name
```

### "500 Internal Server Error"

**Common causes:**
1. Missing dependencies in requirements.txt
2. Python version mismatch
3. API key issues

**Solution:**
Check Vercel function logs and error details

### Slow Performance

**Solutions:**
1. Optimize image sizes before upload
2. Use Vercel Pro for better performance
3. Add caching headers

### Images Not Displaying

**Check:**
1. File paths are correct (use `/css/` not `css/`)
2. Files are in the `public` folder
3. Clear browser cache

## 🎯 Custom Domain (Optional)

Want `fusion.yoursite.com` instead of `vercel.app`?

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Vercel handles SSL automatically!

## 📱 Features of Vercel Deployment

✅ **Global CDN** - Fast worldwide
✅ **Auto-scaling** - Handles traffic spikes
✅ **SSL Certificate** - Automatic HTTPS
✅ **Zero downtime** - Seamless updates
✅ **Serverless** - No server management
✅ **Free tier** - Perfect for most users

## 🔗 Share Your App

Once deployed, share:
- Direct link: `https://your-app.vercel.app`
- Embed in WordPress (iFrame method above)
- Share on social media
- Add to your website navigation

## ✨ Advanced Tips

### Custom Error Messages

Edit `api/merge.py` to add friendly messages:

```python
try:
    # ... your code
except Exception as e:
    error_messages = {
        'quota': 'API quota exceeded. Please try again later.',
        'invalid': 'Invalid API key. Please check your key.',
        'timeout': 'Request timeout. Please try smaller images.'
    }
    # Return appropriate message
```

### Add Google Analytics

Add to `public/index.html` before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-GA-ID');
</script>
```

### CORS Configuration

If accessing from other domains, add to `api/merge.py`:

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": ["https://yoursite.com"]}})
```

## 📞 Need Help?

1. **Check Vercel logs** (most issues show up here)
2. **Test locally first** before deploying
3. **Verify all files are uploaded** to GitHub
4. **Check API key** is valid and has quota

## 🎉 You're Live!

Your AI Image Fusion Studio is now:
- ✅ Publicly accessible
- ✅ Globally fast (CDN)
- ✅ Automatically scaled
- ✅ Secured with HTTPS
- ✅ Free to run!

Share your creation with the world! 🌍✨

---

**Questions?** Check the troubleshooting section or Vercel's documentation at [vercel.com/docs](https://vercel.com/docs)

**Happy deploying! 🚀**
