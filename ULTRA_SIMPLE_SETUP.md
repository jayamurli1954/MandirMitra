# Ultra Simple Setup - Just 2 Commands! 🚀

## ✅ Super Easy - No Copying/Pasting Needed!

I've created a **single script** that does everything automatically!

---

## 📋 Just Follow These 2 Steps:

### Step 1: Activate Your Environment

First, you need to activate the conda environment that has your project installed:

```bash
# Try one of these (whichever environment has your project):
conda activate your_env_name

# OR if you don't know the name, try:
conda activate base
# Then install dependencies if needed
```

**If you're not sure which environment to use:**
- Look for a file called `environment.yml` or `requirements.txt` in your project
- Or ask me and I can help you find it

### Step 2: Run the Setup Script

```bash
# Make sure you're in the backend folder
cd D:\MandirSync\backend

# Run the setup script
python -m scripts.setup_multi_user
```

---

## 🎯 That's It!

The script will automatically:
1. ✅ Create the audit_logs table
2. ✅ Create 3 clerk users (clerk1, clerk2, clerk3)
3. ✅ Show you everything that was created

**No copying, no pasting, no SQL - just run the script!**

---

## 📺 What You'll See:

```
============================================================
MULTI-USER & AUDIT TRAIL SETUP
============================================================

STEP 1: Creating Audit Logs Table...
✅ Audit logs table created successfully!

STEP 2: Creating Clerk Users...
✅ Created: Clerk 1
   Email: clerk1@temple.local
   Password: clerk123

✅ SETUP COMPLETE!
```

---

## ❓ Need Help?

If you get an error, just tell me what the error message says and I'll help you fix it!

---

**Just 2 commands and you're done!** 🎉







