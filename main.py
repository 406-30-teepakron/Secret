import sqlite3
from datetime import date, datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="📚",
    layout="wide"
)

DB_FILE = "study_planner.db"


# --- ส่วนจัดการฐานข้อมูล SQLite ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ยังไม่เสร็จ',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task(subject, title, due_date, priority, notes):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO tasks (subject, title, due_date, priority, status, notes, created_at)
        VALUES (?, ?, ?, ?, 'ยังไม่เสร็จ', ?, ?)
        """,
        (subject, title, str(due_date), priority, notes, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()


def get_tasks():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    return df


def update_task_status(task_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


init_db()

# --- แถบด้านข้าง ---
with st.sidebar:
    st.title("📚 Smart Study Planner")
    st.caption("เว็บแอปพลิเคชันช่วยจัดการการบ้านและวางแผนการเรียน")
    st.divider()
    st.markdown("**จัดทำโดย:** กลุ่มที่ 3")
    st.markdown("**เทคโนโลยี:** Python, Streamlit, SQLite")
    st.info("งานที่เหลือเวลาส่งไม่เกิน 2 วัน จะถูกแจ้งเตือนอัตโนมัติ")

# --- ส่วนหัวหน้าเว็บ ---
st.title("📚 ระบบจัดการการบ้านและวางแผนการเรียน")
st.write("จัดการงานค้าง จัดลำดับความสำคัญ และจับเวลาอ่านหนังสือได้ในที่เดียว")

df = get_tasks()
today = date.today()
priority_order = {"สูง": 1, "ปานกลาง": 2, "ต่ำ": 3}
status_order = {"ยังไม่เสร็จ": 0, "เสร็จแล้ว": 1}

if not df.empty:
    df["due_date_obj"] = pd.to_datetime(df["due_date"]).dt.date
    df["days_left"] = df["due_date_obj"].apply(lambda d: (d - today).days)
    df["priority_rank"] = df["priority"].map(priority_order).fillna(2)
    df["status_rank"] = df["status"].map(status_order).fillna(0)
    df = df.sort_values(
        by=["status_rank", "due_date_obj", "priority_rank"],
        ascending=[True, True, True]
    )

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 รายการการบ้าน",
    "➕ เพิ่มการบ้านใหม่",
    "⏱️ จับเวลาอ่านหนังสือ",
    "📊 สรุปภาพรวม"
])

# แท็บที่ 1: รายการการบ้าน
with tab1:
    if df.empty:
        st.info("ยังไม่มีรายการการบ้าน กดที่แท็บ '➕ เพิ่มการบ้านใหม่' เพื่อเริ่มต้น")
    else:
        urgent_tasks = df[(df["status"] == "ยังไม่เสร็จ") & (df["days_left"] <= 2)]
        if not urgent_tasks.empty:
            st.warning(f"⚠️ มีงานเร่งด่วน (เลยกำหนดหรือเหลือไม่เกิน 2 วัน) จำนวน {len(urgent_tasks)} งาน!")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_status = st.selectbox("กรองตามสถานะ", ["ทั้งหมด", "ยังไม่เสร็จ", "เสร็จแล้ว"])
        with col_f2:
            subjects = ["ทั้งหมด"] + sorted(df["subject"].unique().tolist())
            filter_subject = st.selectbox("กรองตามรายวิชา", subjects)

        filtered_df = df.copy()
        if filter_status != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["status"] == filter_status]
        if filter_subject != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["subject"] == filter_subject]

        st.divider()

        if filtered_df.empty:
            st.write("ไม่พบรายการที่ตรงกับตัวกรอง")
        else:
            for _, row in filtered_df.iterrows():
                days_left = row["days_left"]
                if row["status"] == "เสร็จแล้ว":
                    badge = "✅ เสร็จแล้ว"
                elif days_left < 0:
                    badge = f"🔴 เลยกำหนด {abs(days_left)} วัน"
                elif days_left == 0:
                    badge = "🟠 ส่งวันนี้!"
                elif days_left <= 2:
                    badge = f"🟡 เหลืออีก {days_left} วัน"
                else:
                    badge = f"🟢 เหลืออีก {days_left} วัน"

                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 2, 2])
                    with c1:
                        st.markdown(f"### [{row['subject']}] {row['title']}")
                        st.caption(
                            f"กำหนดส่ง: {row['due_date']} | ความสำคัญ: **{row['priority']}** | {badge}"
                        )
                        if row["notes"]:
                            st.write(f"📝 รายละเอียด: {row['notes']}")
                    with c2:
                        if row["status"] == "ยังไม่เสร็จ":
                            if st.button("✅ ทำเสร็จแล้ว", key=f"done_{row['id']}"):
                                update_task_status(row["id"], "เสร็จแล้ว")
                                st.rerun()
                        else:
                            if st.button("↩️ ย้อนสถานะ", key=f"undo_{row['id']}"):
                                update_task_status(row["id"], "ยังไม่เสร็จ")
                                st.rerun()
                    with c3:
                        if st.button("🗑️ ลบงาน", key=f"del_{row['id']}"):
                            delete_task(row["id"])
                            st.rerun()

# แท็บที่ 2: เพิ่มการบ้านใหม่
with tab2:
    st.subheader("เพิ่มรายการการบ้านหรือภาระงานใหม่")
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox(
                "รายวิชา",
                ["คณิตศาสตร์", "วิทยาศาสตร์", "ภาษาไทย", "ภาษาอังกฤษ", "สังคมศึกษา", "คอมพิวเตอร์", "อื่นๆ"]
            )
            title = st.text_input("ชื่องาน / หัวข้อการบ้าน", placeholder="เช่น แบบฝึกหัดบทที่ 3 หรือ รายงานกลุ่ม")
        with col2:
            due_date = st.date_input("วันกำหนดส่ง", value=today)
            priority = st.select_slider("ระดับความสำคัญ", options=["ต่ำ", "ปานกลาง", "สูง"], value="ปานกลาง")

        notes = st.text_area("รายละเอียดเพิ่มเติม (ถ้ามี)", placeholder="เช่น ส่งผ่าน Google Classroom ก่อน 16.00 น.")
        submitted = st.form_submit_button("💾 บันทึกการบ้าน")

        if submitted:
            if not title.strip():
                st.error("กรุณากรอกชื่องาน / หัวข้อการบ้านก่อนบันทึก")
            else:
                add_task(subject, title.strip(), due_date, priority, notes.strip())
                st.success(f"บันทึกงาน '{title}' เรียบร้อยแล้ว!")
                st.rerun()

# แท็บที่ 3: ตัวจับเวลาอ่านหนังสือ (Pomodoro)
with tab3:
    st.subheader("⏱️ ตัวจับเวลาอ่านหนังสือแบบ Pomodoro")
    st.write("อ่านหนังสือ 25 นาที สลับพักสายตา 5 นาที เพื่อช่วยเพิ่มสมาธิ")

    pomodoro_html = """
    <div style="font-family: sans-serif; text-align: center; padding: 24px; border: 1px solid #ddd; border-radius: 12px; background-color: #f9fafb; max-width: 480px; margin: auto;">
        <h2 id="mode-label" style="margin-top: 0; color: #1f2937;">โหมดอ่านหนังสือ (25 นาที)</h2>
        <div id="timer" style="font-size: 64px; font-weight: bold; color: #ef4444; margin: 16px 0;">25:00</div>
        <div style="margin-bottom: 16px;">
            <button onclick="setMode(25, 'โหมดอ่านหนังสือ (25 นาที)', '#ef4444')" style="padding: 8px 14px; margin: 4px; border-radius: 6px; border: 1px solid #ccc; cursor: pointer;">อ่าน 25 นาที</button>
            <button onclick="setMode(5, 'พักสั้น (5 นาที)', '#10b981')" style="padding: 8px 14px; margin: 4px; border-radius: 6px; border: 1px solid #ccc; cursor: pointer;">พักสั้น 5 นาที</button>
            <button onclick="setMode(15, 'พักยาว (15 นาที)', '#3b82f6')" style="padding: 8px 14px; margin: 4px; border-radius: 6px; border: 1px solid #ccc; cursor: pointer;">พักยาว 15 นาที</button>
        </div>
        <div>
            <button onclick="startTimer()" style="padding: 10px 20px; margin: 4px; background-color: #2563eb; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">▶ เริ่ม</button>
            <button onclick="pauseTimer()" style="padding: 10px 20px; margin: 4px; background-color: #f59e0b; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">⏸ หยุดชั่วคราว</button>
            <button onclick="resetTimer()" style="padding: 10px 20px; margin: 4px; background-color: #6b7280; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">🔄 รีเซ็ต</button>
        </div>
    </div>
    <script>
        let defaultSeconds = 25 * 60;
        let secondsLeft = defaultSeconds;
        let timerInterval = null;

        function updateDisplay() {
            const mins = Math.floor(secondsLeft / 60);
            const secs = secondsLeft % 60;
            document.getElementById('timer').textContent =
                String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
        }

        function setMode(minutes, label, color) {
            pauseTimer();
            defaultSeconds = minutes * 60;
            secondsLeft = defaultSeconds;
            document.getElementById('mode-label').textContent = label;
            document.getElementById('timer').style.color = color;
            updateDisplay();
        }

        function startTimer() {
            if (timerInterval !== null) return;
            timerInterval = setInterval(() => {
                if (secondsLeft > 0) {
                    secondsLeft--;
                    updateDisplay();
                } else {
                    pauseTimer();
                    alert("⏰ หมดเวลาแล้ว!");
                }
            }, 1000);
        }

        function pauseTimer() {
            clearInterval(timerInterval);
            timerInterval = null;
        }

        function resetTimer() {
            pauseTimer();
            secondsLeft = defaultSeconds;
            updateDisplay();
        }
    </script>
    """
    components.html(pomodoro_html, height=300)

# แท็บที่ 4: สรุปภาพรวมและกราฟ
with tab4:
    st.subheader("📊 สรุปภาระงานทั้งหมด")
    if df.empty:
        st.info("ยังไม่มีข้อมูลสำหรับสร้างกราฟ")
    else:
        total_tasks = len(df)
        done_tasks = len(df[df["status"] == "เสร็จแล้ว"])
        pending_tasks = len(df[df["status"] == "ยังไม่เสร็จ"])
        overdue_tasks = len(df[(df["status"] == "ยังไม่เสร็จ") & (df["days_left"] < 0)])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("งานทั้งหมด", total_tasks)
        m2.metric("ยังไม่เสร็จ", pending_tasks)
        m3.metric("เสร็จแล้ว", done_tasks)
        m4.metric("เลยกำหนดส่ง", overdue_tasks)

        st.divider()
        st.markdown("#### จำนวนงานแยกตามรายวิชาและสถานะ")
        chart_data = df.groupby(["subject", "status"]).size().unstack(fill_value=0)
        st.bar_chart(chart_data)

        st.divider()
        csv_data = df[["subject", "title", "due_date", "priority", "status", "notes"]].to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 ดาวน์โหลดรายการการบ้านเป็นไฟล์ CSV",
            data=csv_data,
            file_name="my_study_planner.csv",
            mime="text/csv"
        )
