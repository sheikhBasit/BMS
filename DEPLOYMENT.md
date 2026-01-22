# BookShare - Deploying to Vercel

## Prerequisites
- A Vercel account (sign up at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)
- Your BookShare code pushed to the repository

## Deployment Steps

### 1. Prepare Your Repository
Make sure all files are committed and pushed:
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Import Project to Vercel

#### Option A: Via Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your Git repository
4. Vercel will auto-detect the Flask framework

#### Option B: Via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

### 3. Configure Environment Variables

In the Vercel dashboard, go to your project settings and add:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
CLOUDINARY_CLOUD_NAME=your-cloud-name (if using Cloudinary)
CLOUDINARY_API_KEY=your-api-key (if using Cloudinary)
CLOUDINARY_API_SECRET=your-api-secret (if using Cloudinary)
```

**Generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 4. Database Considerations

⚠️ **Important:** SQLite doesn't work well on Vercel's serverless environment.

You have two options:

#### Option A: Use PostgreSQL (Recommended for Production)
1. Set up a PostgreSQL database (e.g., using Vercel Postgres, Supabase, or Railway)
2. Update `config.py`:
```python
import os
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/bookshare.db')
```
3. Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```
4. Add `DATABASE_URL` to Vercel environment variables

#### Option B: Use Vercel Postgres (Easiest)
1. In Vercel dashboard, go to Storage → Postgres
2. Create a new database
3. Vercel will automatically add environment variables
4. Update `config.py` to use the DATABASE_URL

### 5. File Uploads

Since Vercel is serverless, local file storage (`static/uploads`) won't persist.

**Solutions:**
1. **Use Cloudinary** (already configured in code)
   - Uncomment Cloudinary upload code in `app.py`
   - Add Cloudinary credentials to Vercel env vars

2. **Use Vercel Blob Storage**
   ```bash
   pip install vercel-blob
   ```

3. **Use AWS S3 or similar**

### 6. Deploy!

Once configured, Vercel will auto-deploy on every push to your main branch.

**Manual deployment:**
```bash
vercel --prod
```

### 7. Post-Deployment

After deployment:
1. Visit your app URL (e.g., `your-app.vercel.app`)
2. Create the admin account via seed script or manually
3. Test all features

## Troubleshooting

### Build Fails
- Check `vercel.json` is present
- Verify `requirements.txt` has all dependencies
- Check build logs in Vercel dashboard

### Database Errors
- Ensure DATABASE_URL is set
- For Postgres, ensure tables are created
- Run migrations if using Flask-Migrate

### File Upload Fails
- Switch to Cloudinary or cloud storage
- Vercel's filesystem is read-only

### Static Files Not Loading
- Verify `vercel.json` routes configuration
- Check static file paths are correct

## Important Notes

1. **Serverless Limitations:**
   - No persistent file storage
   - Cold starts may cause initial delay
   - Database connections should use pooling

2. **Free Tier Limits:**
   - Vercel Free: 100 GB bandwidth/month
   - Execution timeout: 10 seconds (Hobby), 60s (Pro)

3. **Database Seeding:**
   - Don't use `seed_db.py` in production
   - Create admin account manually or via migration

## Alternative: Deploy to Railway

If Vercel proves difficult, try Railway (better for databases):

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

Railway provides PostgreSQL out of the box!

## Production Checklist

- [ ] Environment variables set
- [ ] Database configured (PostgreSQL)
- [ ] File uploads use cloud storage
- [ ] SECRET_KEY is secure
- [ ] Debug mode is OFF
- [ ] Admin account created
- [ ] All features tested on production URL

---

**Need Help?** Check Vercel docs: https://vercel.com/docs/frameworks/flask
