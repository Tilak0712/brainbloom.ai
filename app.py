import streamlit as st
from datetime import datetime
import os, json, platform, uuid
from io import BytesIO

from firebase_config import db
from models.auth import login_user, signup_user, reset_password, send_otp_email, generate_otp
from models.chat_model import get_chat_response
from models.image_gen import generate_image
from models.pdf_tool import extract_text_from_pdf
from models.diet_tool import diet_recommendation
from models.math_tool import solve_math
from models.voice_input import transcribe_audio
from models.file_chat import handle_uploaded_file
from models.code_writer import generate_code
from models.token_counter import count_tokens
from models.memory_manager import save_memory, list_memories, load_memory

st.set_page_config(page_title="BrainBloom.AI", layout="wide")

session_file = "user_session.json"
device_id = f"{platform.node()}_{uuid.getnode()}"

if not st.session_state.get("logged_in", False):
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_login = datetime.fromisoformat(data["timestamp"])
            if data.get("device_id") == device_id and (datetime.now() - last_login).total_seconds() < 604800:
                st.session_state.update({
                    "username": data["username"],
                    "role": data["role"],
                    "logged_in": True
                })
                st.success(f"Welcome back, {data['username']}!")
                st.rerun()
            else:
                os.remove(session_file)
    except:
        pass

for k in ["logged_in", "username", "role", "awaiting_otp", "otp_code", "signup_pending", "signup_data"]:
    if k not in st.session_state:
        st.session_state[k] = False if k in ["logged_in", "awaiting_otp", "signup_pending"] else ""

if not st.session_state["logged_in"]:
    st.title("🔐 BrainBloom.AI Access")
    tab1, tab2, tab3 = st.tabs(["🔓 Login", "📝 Sign Up (OTP)", "🔁 Reset Password"])

    with tab1:
        uname = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pass")
        remember = st.checkbox("Remember Me", value=True)

        if st.button("Login"):
            ok, role, email = login_user(uname, pwd)
            if ok:
                st.session_state.update({"logged_in": True, "username": uname, "role": role})
                if remember:
                    with open(session_file, "w", encoding="utf-8") as f:
                        json.dump({
                            "username": uname,
                            "role": role,
                            "email": email,
                            "timestamp": datetime.now().isoformat(),
                            "device_id": device_id
                        }, f)
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        if not st.session_state["awaiting_otp"]:
            u = st.text_input("Username", key="reg_user")
            p = st.text_input("Password", type="password", key="reg_pass")
            r = st.text_input("Recovery Word", key="reg_recovery")
            e = st.text_input("Email", key="reg_email")
            if st.button("Send OTP"):
                if "@" not in e or "." not in e:
                    st.error("Enter valid email")
                else:
                    otp = generate_otp()
                    send_otp_email(e, otp)
                    st.session_state.update({
                        "awaiting_otp": True,
                        "otp_code": otp,
                        "signup_pending": True,
                        "signup_data": {"u": u, "p": p, "r": r, "e": e}
                    })
                    st.success(f"OTP sent to {e}")
        else:
            v = st.text_input("Enter 4-digit OTP", key="reg_otp")
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("🔙 Back"):
                    st.session_state.update({"awaiting_otp": False, "signup_pending": False})
                    st.rerun()
            with col2:
                if st.button("Verify & Sign Up"):
                    if v == st.session_state["otp_code"]:
                        data = st.session_state["signup_data"]
                        if signup_user(data["u"], data["p"], data["r"], data["e"]):
                            st.success("Account created! You can now login.")
                            st.session_state.update({"awaiting_otp": False, "signup_pending": False})
                            st.rerun()
                        else:
                            st.error("Username already exists.")
                    else:
                        st.error("Incorrect OTP")

    with tab3:
        ru = st.text_input("Username", key="reset_user")
        rr = st.text_input("Recovery Word", key="reset_word")
        rn = st.text_input("New Password", type="password", key="reset_new")
        if st.button("Reset Password"):
            if reset_password(ru, rr, rn):
                st.success("Password updated!")
            else:
                st.error("Invalid recovery info")

    st.stop()

USERNAME = st.session_state["username"]
ROLE = st.session_state["role"]

if "chat_title" not in st.session_state:
    st.session_state.update({
        "chat_title": f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "chat_messages": []
    })

if "tool" not in st.session_state:
    st.session_state["tool"] = "Chat"

with st.sidebar:
    st.markdown(f"👤 `{USERNAME}` | Role: `{ROLE}`")
    if st.button("+ New Chat"):
        st.session_state.update({
            "chat_title": f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "chat_messages": []
        })
        st.rerun()

    chats_ref = db.reference(f"chats/{USERNAME}").get() or {}
    chats = sorted(chats_ref.keys(), reverse=True)
    selected_chat = st.selectbox("🕘 Chats", chats, index=chats.index(st.session_state["chat_title"]) if st.session_state["chat_title"] in chats else 0)

    if selected_chat and selected_chat != st.session_state["chat_title"]:
        st.session_state.update({
            "chat_title": selected_chat,
            "chat_messages": chats_ref[selected_chat]
        })

    new_name = st.text_input("Rename Chat", value=st.session_state["chat_title"])
    if new_name and new_name != st.session_state["chat_title"]:
        if st.button("✏️ Rename Chat"):
            db.reference(f"chats/{USERNAME}/{new_name}").set(st.session_state["chat_messages"])
            db.reference(f"chats/{USERNAME}/{st.session_state['chat_title']}").delete()
            st.session_state["chat_title"] = new_name
            st.success("Renamed chat!")
            st.rerun()

    if st.button("📂 Download Chat"):
        chat_data = json.dumps(st.session_state["chat_messages"], indent=2)
        st.download_button("Save JSON", chat_data, file_name=f"{st.session_state['chat_title']}.json")

    upload_chat = st.file_uploader("📂 Upload Chat (.json)", type="json")
    if upload_chat:
        uploaded = json.load(upload_chat)
        if isinstance(uploaded, list) and all("role" in m and "content" in m for m in uploaded):
            st.session_state["chat_messages"] = uploaded
            st.success("Chat restored from file!")

    if st.button("🗑 Delete Chat"):
        db.reference(f"chats/{USERNAME}/{selected_chat}").delete()
        st.success(f"Deleted {selected_chat}")
        st.rerun()

    st.markdown("## 🧠 Memories")
    memories = list_memories(USERNAME)
    sel_mem = st.selectbox("Load Memory", ["-- Select --"] + memories)
    if sel_mem != "-- Select --" and st.button("📂 Load Memory"):
        msgs, meta = load_memory(USERNAME, sel_mem)
        st.session_state["chat_messages"] = msgs
        st.success(f"Memory '{sel_mem}' loaded!")
        st.rerun()

    save_mem_name = st.text_input("Save current chat as memory", value=f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    if st.button("📂 Save Memory"):
        save_memory(USERNAME, save_mem_name, st.session_state["chat_messages"])
        st.success(f"Memory '{save_mem_name}' saved!")
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        if os.path.exists(session_file):
            os.remove(session_file)
        st.rerun()

    st.markdown("## Tools")
    tool = st.radio("Select Tool", ["Chat", "Image Generator", "PDF Q&A", "Diet Planner", "Math Solver", "Voice Input", "Chat with File", "Code Writer"], index=["Chat", "Image Generator", "PDF Q&A", "Diet Planner", "Math Solver", "Voice Input", "Chat with File", "Code Writer"].index(st.session_state["tool"]))
    st.session_state["tool"] = tool

    if ROLE == "admin":
        st.markdown("## 🔠 Admin Tools")
        if st.button("🔍 View All Users"):
            st.json(db.reference("users").get())
        if st.button("📂 View All Chats"):
            st.json(db.reference("chats").get())

def save_chat(title, messages):
    for m in messages:
        if "timestamp" not in m:
            m["timestamp"] = datetime.now().isoformat()
    db.reference(f"chats/{USERNAME}/{title}").set(messages)

# ================== TOOL SELECTION ===================

if st.session_state["tool"] == "Chat":
    st.markdown("## 💬 Chat")
    user_input = st.chat_input("Message BrainBloom AI...")
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if ts := msg.get("timestamp"):
                st.caption(f"🕒 {ts.split('T')[1].split('.')[0]}")
    st.caption(f"🧮 Tokens: {count_tokens(st.session_state['chat_messages'])}")
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()})
        with st.spinner("Thinking..."):
            reply = get_chat_response(st.session_state["chat_messages"])
        st.session_state["chat_messages"].append({"role": "assistant", "content": reply, "timestamp": datetime.now().isoformat()})
        save_chat(st.session_state["chat_title"], st.session_state["chat_messages"])
        st.rerun()

elif st.session_state["tool"] == "Image Generator":
    st.header("🎨 Image Generator")
    prompt = st.text_input("Describe the image:")
    if st.button("Generate"):
        with st.spinner("Generating image..."):
            img = generate_image(prompt)
        if isinstance(img, str):  # error message
            st.error(img)
        else:
            st.image(img)
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.download_button("Download PNG", buf.getvalue(), "generated.png")

elif st.session_state["tool"] == "PDF Q&A":
    st.header("📄 PDF Q&A")
    uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_pdf:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_pdf.read())
        res = extract_text_from_pdf("temp.pdf")
        st.text_area("Extracted Text:", res["text"], height=300)
        q = st.text_input("Ask a question:")
        if q:
            ans = get_chat_response([
                {"role": "system", "content": "Answer from this PDF."},
                {"role": "user", "content": f'{res["text"]}\n\nQ: {q}'}
            ])
            st.success(ans)
        os.remove("temp.pdf")

elif st.session_state["tool"] == "Diet Planner":
    st.header("🥗 Diet Planner")
    goal = st.text_input("Your goal:")
    if goal:
        st.write(diet_recommendation(goal))

elif st.session_state["tool"] == "Math Solver":
    st.header("➕ Math Solver")
    eq = st.text_input("Equation:")
    if eq:
        st.success(f"Result: {solve_math(eq)}")

elif st.session_state["tool"] == "Voice Input":
    st.header("🎤 Voice Input")
    audio = st.file_uploader("Upload audio:", type=["wav", "mp3"])
    if audio:
        st.success(transcribe_audio(audio))

elif st.session_state["tool"] == "Chat with File":
    st.header("📁 Chat with File")
    f = st.file_uploader("Upload file:", type=["txt", "pdf", "py", "jpg", "png"])
    q = st.text_input("Ask question:")
    if f and q:
        st.success(handle_uploaded_file(f, q))

elif st.session_state["tool"] == "Code Writer":
    st.header("💻 Code Generator")
    task = st.text_area("Describe code task:")
    if st.button("Generate Code"):
        st.code(generate_code(task), language="python")
