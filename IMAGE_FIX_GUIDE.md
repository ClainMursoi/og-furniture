# Image Upload Fix Guide

## What Was Fixed

### 1. **File Save Location** (`app/routes/admin.py`)
- Files are now saved to the correct absolute path using Flask's config
- Files get unique UUID names to prevent overwrites: `uuid_filename.ext`
- Upload folder is created automatically if it doesn't exist

### 2. **Flask Static Configuration** (`app/__init__.py`)
- Explicit static folder path set: `app/static`
- Static URL path: `/static`
- Both configured as absolute paths for reliability

### 3. **Image URL Generation** (`app/routes/admin.py`)
- Uses Flask's `url_for()` to generate correct paths
- Generates URLs like: `/static/uploads/uuid_filename.ext`
- URLs are stored in the database

## Testing the Fix

### Test 1: Check Static File Configuration
Visit this endpoint in your browser:
```
http://localhost:5000/test-static
```

This will show:
- Static folder location
- Upload folder location  
- Files in the uploads folder
- Example static URL format

### Test 2: Upload a New Product
1. Go to Admin → Add New Product
2. Fill in product details
3. Upload images (up to 4)
4. Submit

### Test 3: View the Product
1. Go to the customer homepage
2. Look for the newly added product
3. Images should display in the "Available in Store" section
4. Try clicking next/prev on the product image slider

## If Images Still Don't Show

### Check the browser console:
1. Open Developer Tools (F12)
2. Look at the Console tab
3. Check if there are 404 errors for image URLs
4. Look at the Network tab to see what URL is being requested

### Check actual file locations:
Files should be saved in: `app/static/uploads/`

You can verify files are there with:
```powershell
Get-ChildItem 'app/static/uploads'
```

### Common Issues

**Issue 1: 404 errors for images**
- Files exist but Flask isn't serving them
- Try restarting the Flask app

**Issue 2: Images uploaded but appear blank**
- Check the database to see what URL is stored
- Should be format: `/static/uploads/uuid_filename.ext`

**Issue 3: Old products still don't show images**
- Old products may have incorrect paths stored
- New products should work with the updated code

## Fixing Old Products

If old products have broken image paths, you have two options:

### Option A: Re-upload their images
1. Delete the old product
2. Create it again with the correct images

### Option B: Database migration (Advanced)
If you need to keep old products, contact support for a database migration script.
