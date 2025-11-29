# Simple Setup - Just One Command! 🚀

## ✅ Super Simple Method

Since you're not comfortable with copying/pasting SQL, I've created a **single script that does everything**!

### Just Run This One Command:

```bash
cd D:\MandirSync\backend
python -m scripts.setup_multi_user
```

That's it! The script will:
1. ✅ Create the audit_logs table automatically
2. ✅ Create 3 clerk users automatically
3. ✅ Show you everything that was created

---

## 📋 Step-by-Step (Very Simple)

### Step 1: Open Terminal/PowerShell

You're already in the right place! Just make sure you're in the backend folder:

```bash
cd D:\MandirSync\backend
```

### Step 2: Run the Setup Script

```bash
python -m scripts.setup_multi_user
```

### Step 3: Wait for It to Finish

The script will show you:
- ✅ What it's doing
- ✅ What was created
- ✅ Any errors (if any)

### Step 4: Done!

You'll see a message like:
```
✅ SETUP COMPLETE!

Clerk users created:
  - clerk1@temple.local / Password: clerk123
  - clerk2@temple.local / Password: clerk123
  - clerk3@temple.local / Password: clerk123
```

---

## 🎯 That's It!

No copying, no pasting, no SQL - just one command!

---

## ❓ What If It Doesn't Work?

If you get an error like "ModuleNotFoundError", you might need to activate your environment first:

```bash
# If using conda
conda activate your_env_name

# Then run the script
python -m scripts.setup_multi_user
```

---

**That's all you need to do!** 🎉









