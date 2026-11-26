import json
import os
import time
from datetime import date, datetime
import pandas as pd
import streamlit as st

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="📚",
    layout="wide"
)

DATA_FILE = "study_planner_data.json"

DEFAULT_TIMETABLE = [
    {"วัน": "วันจันทร์", "คาบ 1": "", "คาบ 2": "", "คาบ 3": "", "คาบ 4": "", "คาบ 5": "", "คาบ 6": "", "คาบ 7": "", "คาบ 8": ""},
    {"วัน": "วันอังคาร", "คาบ 1": "", "คาบ 2": "", "คาบ 3": "", "คาบ 4": "", "คาบ 5": "", "คาบ 6": "", "คาบ 7": "", "คาบ 8": ""},
    {"วัน": "วันพุธ", "คาบ 1": "", "คาบ 2": "", "คาบ 3": "", "คาบ 4": "", "คาบ 5": "", "คาบ 6": "", "คาบ 7": "", "คาบ 8": ""},
    {"วัน": "วันพฤหัสบดี", "คาบ 1": "", "คาบ 2": "", "คาบ 3": "", "คาบ 4": "", "คาบ 5": "", "คาบ 6": "", "คาบ 7": "", "คาบ 8": ""},
    {"วัน": "วันศุกร์", "คาบ 1": "", "คาบ 2": "", "คาบ 3": "", "คาบ 4": "", "คาบ 5": "", "คาบ 6": "", "คาบ 7": "", "คาบ 8": ""},
]

DEFAULT_GPA_COURSES = [
    {"รายวิชา": "คณิตศาสตร์", "หน่วยกิต": 1.5, "เกรด": 3.5},
    {"รายวิชา": "วิทยาศาสตร์", "หน่วยกิต": 1.5, "เกรด": 3.0},
    {"รายวิชา": "ภาษาไทย", "หน่วยกิต": 1.0, "เกรด": 4.0},
    {"รายวิชา": "ภาษาอังกฤษ", "หน่วยกิต": 1.0, "เกรด": 3.0},
    {"รายวิชา": "คอมพิวเตอร์", "หน่วยกิต": 1.0, "เกรด": 4.0},
]

SUBJECT_OPTIONS = [
    "คณิตศาสตร์",
    "วิทยาศาสตร์",
    "ภาษาไทย",
    "ภาษาอังกฤษ",
    "สังคมศึกษา",
    "คอมพิวเตอร์",
    "สุขศึกษาและพลศึกษา",
    "ศิลปะ",
    "การงานอาชีพ",
    "อื่นๆ",
]


# --- ส่วนจัดการข้อมูลด้วย Python ล้วน (JSON) ---
def get_default_data():
    return {
        "next_task_id": 1,
        "next_exam_id": 1,
        "tasks": [],
        "exams": [],
        "timetable": [row.copy() for row in DEFAULT_TIMETABLE],
        "gpa_courses": [row.copy() for row in DEFAULT_GPA_COURSES],
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        data = get_default_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = get_default_data()
        save_data(data)
        return data

    default_data = get_default_data()
    for key, value in default_data.items():
        if key not in data:
            data[key] = value
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_task(subject, title, due_date, priority, notes):
    data = load_data()
    task_id = data["next_task_id"]
    data["next_task_id"] += 1
    data["tasks"].append({
        "id": task_id,
        "subject": subject,
        "title": title,
        "due_date": str(due_date),
        "priority": priority,
        "status": "ยังไม่เสร็จ",
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data(data)


def update_task_status(task_id, new_status):
    data = load_data()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = new_status
            break
    save_data(data)


def delete_task(task_id):
    data = load_data()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    save_data(data)


def add_exam(exam_type, subject, exam_date, topics):
    data = load_data()
    exam_id = data["next_exam_id"]
    data["next_exam_id"] += 1
    data["exams"].append({
        "id": exam_id,
        "exam_type": exam_type,
        "subject": subject,
        "exam_date": str(exam_date),
        "topics": topics,
    })
    save_data(data)


def delete_exam(exam_id):
    data = load_data()
    data["exams"] = [e for e in data["exams"] if e["id"] != exam_id]
    save_data(data)


def save_timetable(rows):
    data = load_data()
    data["timetable"] = rows
    save_data(data)


def save_gpa_courses(rows):
    data = load_data()
    data["gpa_courses"] = rows
    save_data(data)


# โหลดข้อมูลทั้งหมด
app_data = load_data()
today = date.today()

# เตรียมข้อมูลการบ้าน
tasks_df = pd.DataFrame(app_data["tasks"])
priority_order = {"สูง": 1, "ปานกลาง": 2, "ต่ำ": 3}
status_order = {"ยังไม่เสร็จ": 0, "เสร็จแล้ว": 1}

if not tasks_df.empty:
    tasks_df["due_date_obj"] = pd.to_datetime(tasks_df["due_date"]).dt.date
    tasks_df["days_left"] = tasks_df["due_date_obj"].apply(lambda d: (d - today).days)
    tasks_df["priority_rank"] = tasks_df["priority"].map(priority_order).fillna(2)
    tasks_df["status_rank"] = tasks_df["status"].map(status_order).fillna(0)
    tasks_df = tasks_df.sort_values(
        by=["status_rank", "due_date_obj", "priority_rank"],
        ascending=[True, True, True]
    )

# เตรียมข้อมูลวันสอบ
exams_df = pd.DataFrame(app_data["exams"])
if not exams_df.empty:
    exams_df["exam_date_obj"] = pd.to_datetime(exams_df["exam_date"]).dt.date
    exams_df["days_left"] = exams_df["exam_date_obj"].apply(lambda d: (d - today).days)
    exams_df = exams_df.sort_values(by=["days_left"], ascending=[True])

# --- แถบด้านข้าง ---
with st.sidebar:
    st.title("📚 Smart Study Planner")
    st.caption("เว็บแอปพลิเคชันช่วยจัดการการบ้านและวางแผนการเรียน")
    st.divider()
    st.markdown("**จัดทำโดย:** กลุ่มที่ 3")
    st.info("งานที่เหลือเวลาส่งไม่เกิน 2 วัน จะถูกแจ้งเตือนอัตโนมัติ")

    if not exams_df.empty:
        upcoming_exams = exams_df[exams_df["days_left"] >= 0]
        if not upcoming_exams.empty:
            nearest = upcoming_exams.iloc[0]
            st.divider()
            st.subheader("🗓️ สอบที่ใกล้ที่สุด")
            days_text = "สอบวันนี้!" if nearest["days_left"] == 0 else f"อีก {nearest['days_left']} วัน"
            st.metric(
                label=f"{nearest['exam_type']} - {nearest['subject']}",
                value=days_text,
                delta=f"วันที่ {nearest['exam_date']}"
            )

# --- ส่วนหัวหน้าเว็บ ---
st.title("📚 ระบบจัดการการบ้านและวางแผนการเรียน")
st.write("จัดการการบ้าน นับถอยหลังวันสอบ ดูตารางเรียน คำนวณเกรดเฉลี่ย และจับเวลาอ่านหนังสือได้ครบในที่เดียว")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📋 รายการการบ้าน",
    "➕ เพิ่มการบ้าน",
    "🗓️ นับถอยหลังวันสอบ",
    "📅 ตารางเรียน",
    "🎓 คำนวณเกรดเฉลี่ย",
    "⏱️ จับเวลาอ่านหนังสือ",
    "📊 สรุปภาพรวม"
])

# ==========================================
# แท็บที่ 1: รายการการบ้าน
# ==========================================
with tab1:
    if tasks_df.empty:
        st.info("ยังไม่มีรายการการบ้าน กดที่แท็บ '➕ เพิ่มการบ้าน' เพื่อเริ่มต้นใช้งาน")
    else:
        urgent_tasks = tasks_df[(tasks_df["status"] == "ยังไม่เสร็จ") & (tasks_df["days_left"] <= 2)]
        if not urgent_tasks.empty:
            st.warning(f"⚠️ มีงานเร่งด่วน (เลยกำหนดหรือเหลือไม่เกิน 2 วัน) จำนวน {len(urgent_tasks)} งาน!")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_status = st.selectbox("กรองตามสถานะ", ["ทั้งหมด", "ยังไม่เสร็จ", "เสร็จแล้ว"])
        with col_f2:
            subjects = ["ทั้งหมด"] + sorted(tasks_df["subject"].unique().tolist())
            filter_subject = st.selectbox("กรองตามรายวิชา", subjects)

        filtered_df = tasks_df.copy()
        if filter_status != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["status"] == filter_status]
        if filter_subject != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["subject"] == filter_subject]

        st.divider()

        if filtered_df.empty:
            st.write("ไม่พบรายการที่ตรงกับตัวกรอง")
        else:
            for _, row in filtered_df.iterrows():
                days_left = int(row["days_left"])
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
                                update_task_status(int(row["id"]), "เสร็จแล้ว")
                                st.rerun()
                        else:
                            if st.button("↩️ ย้อนสถานะ", key=f"undo_{row['id']}"):
                                update_task_status(int(row["id"]), "ยังไม่เสร็จ")
                                st.rerun()
                    with c3:
                        if st.button("🗑️ ลบงาน", key=f"del_{row['id']}"):
                            delete_task(int(row["id"]))
                            st.rerun()

# ==========================================
# แท็บที่ 2: เพิ่มการบ้านใหม่
# ==========================================
with tab2:
    st.subheader("เพิ่มรายการการบ้านหรือภาระงานใหม่")
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("รายวิชา", SUBJECT_OPTIONS)
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
                st.success(f"บันทึกงาน '{title.strip()}' เรียบร้อยแล้ว!")
                st.rerun()

# ==========================================
# แท็บที่ 3: นับถอยหลังวันสอบ (Exam Countdown)
# ==========================================
with tab3:
    st.subheader("🗓️ นับถอยหลังวันสอบและหัวข้อที่ออกสอบ")
    st.write("บันทึกวันสอบกลางภาค/ปลายภาค พร้อมจดหัวข้อที่จะออกสอบในแต่ละวิชาเพื่อวางแผนอ่านหนังสือล่วงหน้า")

    with st.expander("➕ เพิ่มกำหนดการสอบใหม่", expanded=exams_df.empty):
        with st.form("add_exam_form", clear_on_submit=True):
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                exam_type = st.selectbox("ประเภทการสอบ", ["สอบกลางภาค", "สอบปลายภาค", "สอบย่อย / เก็บคะแนน"])
            with ec2:
                exam_subject = st.selectbox("รายวิชาที่สอบ", SUBJECT_OPTIONS, key="exam_subject")
            with ec3:
                exam_date = st.date_input("วันสอบ", value=today, key="exam_date")

            exam_topics = st.text_area(
                "หัวข้อที่จะออกสอบ / เนื้อหาที่ต้องอ่าน",
                placeholder="เช่น บทที่ 1 เซต, บทที่ 2 ตรรกศาสตร์, เน้นทำโจทย์ท้ายบทหน้า 45"
            )
            exam_submit = st.form_submit_button("💾 บันทึกวันสอบ")

            if exam_submit:
                add_exam(exam_type, exam_subject, exam_date, exam_topics.strip())
                st.success(f"บันทึกวันสอบวิชา {exam_subject} เรียบร้อยแล้ว!")
                st.rerun()

    st.divider()

    if exams_df.empty:
        st.info("ยังไม่มีข้อมูลวันสอบ ลองเพิ่มกำหนดการสอบด้านบนได้เลย")
    else:
        upcoming_df = exams_df[exams_df["days_left"] >= 0]
        if not upcoming_df.empty:
            st.markdown("#### ⏳ กล่องนับถอยหลังวันสอบที่กำลังจะมาถึง")
            cols = st.columns(min(3, len(upcoming_df)))
            for idx, (_, ex) in enumerate(upcoming_df.head(3).iterrows()):
                d_left = int(ex["days_left"])
                countdown_label = "สอบวันนี้!" if d_left == 0 else f"อีก {d_left} วัน"
                with cols[idx]:
                    with st.container(border=True):
                        st.metric(
                            label=f"{ex['exam_type']} | {ex['subject']}",
                            value=countdown_label,
                            delta=f"วันสอบ: {ex['exam_date']}"
                        )

        st.markdown("#### 📖 รายละเอียดและหัวข้อที่ออกสอบทั้งหมด")
        for _, ex in exams_df.iterrows():
            d_left = int(ex["days_left"])
            if d_left < 0:
                status_text = f"⚪ สอบผ่านไปแล้ว {abs(d_left)} วัน"
            elif d_left == 0:
                status_text = "🔴 สอบวันนี้!"
            elif d_left <= 3:
                status_text = f"🔴 เหลืออีก {d_left} วัน (ใกล้มาก!)"
            elif d_left <= 7:
                status_text = f"🟡 เหลืออีก {d_left} วัน"
            else:
                status_text = f"🟢 เหลืออีก {d_left} วัน"

            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.markdown(f"### [{ex['exam_type']}] วิชา{ex['subject']}")
                    st.caption(f"วันสอบ: {ex['exam_date']} | {status_text}")
                    if ex["topics"]:
                        st.write(f"📌 **หัวข้อที่ออกสอบ:** {ex['topics']}")
                    else:
                        st.caption("ยังไม่ได้ระบุหัวข้อที่ออกสอบ")
                with c2:
                    if st.button("🗑️ ลบ", key=f"del_exam_{ex['id']}"):
                        delete_exam(int(ex["id"]))
                        st.rerun()

# ==========================================
# แท็บที่ 4: ตารางเรียนประจำสัปดาห์ (Class Timetable)
# ==========================================
with tab4:
    st.subheader("📅 ตารางเรียนประจำสัปดาห์ (จันทร์ – ศุกร์)")
    st.write("คลิกที่ช่องในตารางเพื่อพิมพ์ชื่อวิชาในแต่ละคาบ แล้วกดปุ่มบันทึกเพื่อเก็บไว้ดูควบคู่กับการวางแผนทำการบ้าน")

    timetable_df = pd.DataFrame(app_data["timetable"])
    edited_timetable = st.data_editor(
        timetable_df,
        use_container_width=True,
        hide_index=True,
        disabled=["วัน"],
        key="timetable_editor"
    )

    tc1, tc2 = st.columns([2, 2])
    with tc1:
        if st.button("💾 บันทึกตารางเรียน", type="primary"):
            cleaned_rows = edited_timetable.fillna("").to_dict(orient="records")
            save_timetable(cleaned_rows)
            st.success("บันทึกตารางเรียนเรียบร้อยแล้ว!")
            st.rerun()
    with tc2:
        if st.button("🔄 ล้างตารางเรียนทั้งหมด"):
            save_timetable([row.copy() for row in DEFAULT_TIMETABLE])
            st.info("ล้างข้อมูลตารางเรียนแล้ว")
            st.rerun()

# ==========================================
# แท็บที่ 5: เครื่องคำนวณเกรดเฉลี่ย (GPA Calculator)
# ==========================================
with tab5:
    st.subheader("🎓 เครื่องคำนวณเกรดเฉลี่ยประจำเทอม (GPA Calculator)")
    st.write("เพิ่มหรือแก้ไขรายวิชา หน่วยกิต และเกรดที่คาดว่าจะได้ เพื่อดูเกรดเฉลี่ยและวางแผนว่าควรเร่งทำคะแนนวิชาไหนเพิ่ม")

    gpa_df = pd.DataFrame(app_data["gpa_courses"])
    edited_gpa = st.data_editor(
        gpa_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "รายวิชา": st.column_config.TextColumn("รายวิชา", required=True),
            "หน่วยกิต": st.column_config.NumberColumn(
                "หน่วยกิต", min_value=0.5, max_value=5.0, step=0.5, default=1.0, required=True
            ),
            "เกรด": st.column_config.SelectboxColumn(
                "เกรด (0.0 - 4.0)",
                options=[4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.0],
                default=3.5,
                required=True
            ),
        },
        key="gpa_editor"
    )

    if st.button("💾 บันทึกข้อมูลรายวิชาและเกรด", type="primary"):
        valid_save = edited_gpa.dropna(subset=["รายวิชา", "หน่วยกิต", "เกรด"])
        valid_save = valid_save[valid_save["รายวิชา"].astype(str).str.strip() != ""]
        save_gpa_courses(valid_save.to_dict(orient="records"))
        st.success("บันทึกข้อมูลรายวิชาเรียบร้อยแล้ว!")
        st.rerun()

    st.divider()

    valid_gpa = edited_gpa.dropna(subset=["รายวิชา", "หน่วยกิต", "เกรด"]).copy()
    valid_gpa = valid_gpa[valid_gpa["รายวิชา"].astype(str).str.strip() != ""]

    if valid_gpa.empty:
        st.info("กรุณาเพิ่มรายวิชาอย่างน้อย 1 วิชาเพื่อคำนวณเกรดเฉลี่ย")
    else:
        valid_gpa["หน่วยกิต"] = pd.to_numeric(valid_gpa["หน่วยกิต"], errors="coerce").fillna(0.0)
        valid_gpa["เกรด"] = pd.to_numeric(valid_gpa["เกรด"], errors="coerce").fillna(0.0)
        valid_gpa["คะแนนรวม"] = valid_gpa["หน่วยกิต"] * valid_gpa["เกรด"]

        total_credits = float(valid_gpa["หน่วยกิต"].sum())
        total_points = float(valid_gpa["คะแนนรวม"].sum())
        gpa = total_points / total_credits if total_credits > 0 else 0.0

        gm1, gm2, gm3 = st.columns(3)
        gm1.metric("จำนวนรายวิชา", len(valid_gpa))
        gm2.metric("หน่วยกิตรวม", f"{total_credits:.1f}")
        gm3.metric("เกรดเฉลี่ย (GPA)", f"{gpa:.2f}")

        target_gpa = st.slider("🎯 ตั้งเป้าหมายเกรดเฉลี่ยที่ต้องการ", min_value=1.00, max_value=4.00, value=3.50, step=0.05)
        if gpa >= target_gpa:
            st.success(f"เยี่ยมมาก! เกรดเฉลี่ยปัจจุบัน ({gpa:.2f}) ถึงเป้าหมาย ({target_gpa:.2f}) แล้ว")
        else:
            gap_points = (target_gpa * total_credits) - total_points
            st.warning(f"ยังขาดอีก {target_gpa - gpa:.2f} เพื่อให้ถึงเป้า {target_gpa:.2f} (ต้องเพิ่มผลรวมหน่วยกิต×เกรดอีกประมาณ {gap_points:.2f})")

            improvable = valid_gpa[valid_gpa["เกรด"] < 4.0].copy()
            if not improvable.empty:
                improvable["ผลกระทบต่อเกรด"] = (4.0 - improvable["เกรด"]) * improvable["หน่วยกิต"]
                improvable = improvable.sort_values(by=["ผลกระทบต่อเกรด", "เกรด"], ascending=[False, True])
                st.markdown("#### 💡 วิชาที่ควรเร่งทำคะแนนเพิ่ม (เรียงตามความคุ้มค่าต่อ GPA)")
                for _, subj in improvable.head(3).iterrows():
                    boost_half = (0.5 * subj["หน่วยกิต"]) / total_credits if total_credits > 0 else 0.0
                    next_grade = min(4.0, subj["เกรด"] + 0.5)
                    st.write(
                        f"- **วิชา{subj['รายวิชา']}** (หน่วยกิต {subj['หน่วยกิต']:.1f}, เกรดปัจจุบัน {subj['เกรด']:.1f}) "
                        f"→ หากเพิ่มเป็น **{next_grade:.1f}** เกรดเฉลี่ยจะเพิ่มขึ้น **+{boost_half:.2f}** (เป็น {gpa + boost_half:.2f})"
                    )

        st.markdown("#### 📈 กราฟเปรียบเทียบเกรดแต่ละรายวิชา")
        chart_gpa = valid_gpa.groupby("รายวิชา", as_index=True)[["เกรด"]].mean()
        st.bar_chart(chart_gpa)

# ==========================================
# แท็บที่ 6: ตัวจับเวลาอ่านหนังสือ (Pomodoro - Python 100%)
# ==========================================
with tab6:
    st.subheader("⏱️ ตัวจับเวลาอ่านหนังสือแบบ Pomodoro")
    st.write("อ่านหนังสือ 25 นาที สลับพักสายตา 5 นาที เพื่อช่วยเพิ่มสมาธิ")

    if "pomo_duration" not in st.session_state:
        st.session_state.pomo_duration = 25 * 60
    if "pomo_remaining" not in st.session_state:
        st.session_state.pomo_remaining = 25 * 60
    if "pomo_running" not in st.session_state:
        st.session_state.pomo_running = False
    if "pomo_end_time" not in st.session_state:
        st.session_state.pomo_end_time = None
    if "pomo_mode_name" not in st.session_state:
        st.session_state.pomo_mode_name = "โหมดอ่านหนังสือ (25 นาที)"

    def set_pomodoro_mode(minutes, mode_name):
        st.session_state.pomo_running = False
        st.session_state.pomo_end_time = None
        st.session_state.pomo_duration = minutes * 60
        st.session_state.pomo_remaining = minutes * 60
        st.session_state.pomo_mode_name = mode_name

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        if st.button("📖 อ่าน 25 นาที", use_container_width=True):
            set_pomodoro_mode(25, "โหมดอ่านหนังสือ (25 นาที)")
    with mc2:
        if st.button("☕ พักสั้น 5 นาที", use_container_width=True):
            set_pomodoro_mode(5, "พักสั้น (5 นาที)")
    with mc3:
        if st.button("🌿 พักยาว 15 นาที", use_container_width=True):
            set_pomodoro_mode(15, "พักยาว (15 นาที)")

    @st.fragment(run_every=1)
    def pomodoro_display():
        if st.session_state.pomo_running and st.session_state.pomo_end_time is not None:
            left = int(round(st.session_state.pomo_end_time - time.time()))
            if left <= 0:
                st.session_state.pomo_remaining = 0
                st.session_state.pomo_running = False
                st.session_state.pomo_end_time = None
                st.balloons()
                st.success("⏰ หมดเวลาแล้ว! พักสายตาหรือเริ่มรอบถัดไปได้เลย")
            else:
                st.session_state.pomo_remaining = left

        mins, secs = divmod(st.session_state.pomo_remaining, 60)
        elapsed_ratio = 1.0 - (st.session_state.pomo_remaining / st.session_state.pomo_duration) if st.session_state.pomo_duration > 0 else 1.0
        elapsed_ratio = max(0.0, min(1.0, elapsed_ratio))

        with st.container(border=True):
            st.markdown(f"### {st.session_state.pomo_mode_name}")
            st.metric("เวลาที่เหลือ", f"{mins:02d}:{secs:02d}")
            st.progress(elapsed_ratio)

            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                if st.button("▶ เริ่มจับเวลา", use_container_width=True, disabled=st.session_state.pomo_running):
                    if st.session_state.pomo_remaining == 0:
                        st.session_state.pomo_remaining = st.session_state.pomo_duration
                    st.session_state.pomo_end_time = time.time() + st.session_state.pomo_remaining
                    st.session_state.pomo_running = True
                    st.rerun()
            with bc2:
                if st.button("⏸ หยุดชั่วคราว", use_container_width=True, disabled=not st.session_state.pomo_running):
                    if st.session_state.pomo_end_time is not None:
                        st.session_state.pomo_remaining = max(0, int(round(st.session_state.pomo_end_time - time.time())))
                    st.session_state.pomo_running = False
                    st.session_state.pomo_end_time = None
                    st.rerun()
            with bc3:
                if st.button("🔄 รีเซ็ต", use_container_width=True):
                    st.session_state.pomo_running = False
                    st.session_state.pomo_end_time = None
                    st.session_state.pomo_remaining = st.session_state.pomo_duration
                    st.rerun()

    pomodoro_display()

# ==========================================
# แท็บที่ 7: สรุปภาพรวมและกราฟ
# ==========================================
with tab7:
    st.subheader("📊 สรุปภาระงานทั้งหมด")
    if tasks_df.empty:
        st.info("ยังไม่มีข้อมูลการบ้านสำหรับสร้างกราฟ")
    else:
        total_tasks = len(tasks_df)
        done_tasks = len(tasks_df[tasks_df["status"] == "เสร็จแล้ว"])
        pending_tasks = len(tasks_df[tasks_df["status"] == "ยังไม่เสร็จ"])
        overdue_tasks = len(tasks_df[(tasks_df["status"] == "ยังไม่เสร็จ") & (tasks_df["days_left"] < 0)])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("งานทั้งหมด", total_tasks)
        m2.metric("ยังไม่เสร็จ", pending_tasks)
        m3.metric("เสร็จแล้ว", done_tasks)
        m4.metric("เลยกำหนดส่ง", overdue_tasks)

        st.divider()
        st.markdown("#### จำนวนงานแยกตามรายวิชาและสถานะ")
        chart_data = tasks_df.groupby(["subject", "status"]).size().unstack(fill_value=0)
        st.bar_chart(chart_data)

        st.divider()
        csv_data = tasks_df[["subject", "title", "due_date", "priority", "status", "notes"]].to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 ดาวน์โหลดรายการการบ้านเป็นไฟล์ CSV",
            data=csv_data,
            file_name="my_study_planner.csv",
            mime="text/csv"
        )
