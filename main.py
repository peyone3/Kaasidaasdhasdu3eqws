from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters,
)
import logging
import asyncio
import nest_asyncio
import os
from keep_alive import keep_alive
keep_alive()


# Enable logging for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

(
    LANGUAGE,
    MAIN_MENU,
    INTERNAL_SEMESTER,
    INTERNAL_SUBJECT,
    INTERNAL_COURSE_TYPE,
    INTERNAL_GRADE_INPUT,
    FINAL_INTERNAL_SCORE,
    FINAL_TOTAL_QUESTIONS,
    FINAL_PASS_PERCENT,
    GPA_GRADE_INPUT,
) = range(10)

semesters = {
    "ar": {
        "السمستر الأول": [
            "الإنجليزية",
            "التواصل الصحي بالعربية",
            "أساسيات التمريض 1",
            "أساسيات التمريض 1 (عملي)",
            "التشريح",
            "الفسيولوجيا",
            "التغذية والنظام الغذائي",
        ],
        "السمستر الثاني": [
            "التواصل الصحي بالإنجليزية",
            "الميكروبيولوجي",
            "أساسيات التمريض 2",
            "أساسيات التمريض 2 (عملي)",
            "التشريح (متابعة)",
            "الفسيولوجيا (متابعة)",
        ],
        "السمستر الثالث": [
            "التقييم الصحي",
            "التقييم الصحي (عملي)",
            "علم الأدوية في التمريض",
            "الكيمياء الحيوية البشرية",
            "الفيزيولوجيا المرضية",
            "التمريض الصحي للكبار 1",
            "التمريض الصحي للكبار 1 (عملي)",
        ],
        "السمستر الرابع": [
            "علم النفس",
            "علم الأدوية في التمريض (متابعة)",
            "الثقافة الإسلامية والطب",
            "التمريض الصحي للكبار 1 (متابعة)",
            "التمريض الصحي للكبار 1 (عملي)",
            "جمعية الإمارات",
            "معلوماتية الصحة والتكنولوجيا",
        ],
        "السمستر الخامس": [
            "تعليم التمريض",
            "تمريض الأطفال",
            "تمريض الصحة النفسية والطب النفسي",
            "التمريض الصحي للكبار 2",
            "القيادة والإدارة في التمريض",
            "القضايا المهنية والاتجاهات في التمريض",
            "القضايا القانونية والأخلاقية في التمريض",
            "التمريض النسائي",
        ],
        "السمستر السادس": [
            "تعليم التمريض (متابعة)",
            "تمريض الأطفال (متابعة)",
            "تمريض الصحة النفسية والطب النفسي (متابعة)",
            "التمريض الصحي للكبار 2 (متابعة)",
            "القيادة والإدارة في التمريض (متابعة)",
            "القضايا المهنية والاتجاهات في التمريض (متابعة)",
            "القضايا القانونية والأخلاقية في التمريض (متابعة)",
        ],
        "السمستر السابع": [
            "التمريض التوليدي",
            "تمريض العناية الحرجة",
            "تمريض الصحة المجتمعية",
            "التدريب السريري",
        ],
        "السمستر الثامن": [
            "التمريض التوليدي (متابعة)",
            "تمريض العناية الحرجة (متابعة)",
            "تمريض الصحة المجتمعية (متابعة)",
            "التدريب السريري الاختياري",
            "منهجية البحث والاحصاء في التمريض",
        ],
    },
    "en": {
        "Semester 1": [
            "English",
            "Health Sciences Communication in Arabic",
            "Foundations of Nursing Practice-1",
            "Foundations of Nursing Practice-1 (Practical)",
            "Anatomy",
            "Physiology",
            "Nutrition & Dietetics",
        ],
        "Semester 2": [
            "Health Sciences Communication in English",
            "Microbiology",
            "Foundations of Nursing Practice-2",
            "Foundations of Nursing Practice-2 (Practical)",
            "Anatomy (Contd.)",
            "Physiology (Contd.)",
        ],
        "Semester 3": [
            "Health Assessment",
            "Health Assessment (Practical)",
            "Pharmacology in Nursing",
            "Human Biochemistry",
            "Pathophysiology",
            "Adult Health Nursing 1",
            "Adult Health Nursing 1 (Practical)",
        ],
        "Semester 4": [
            "Psychology",
            "Pharmacology in Nursing (Contd.)",
            "Islamic Culture & Medicine",
            "Adult Health Nursing 1 (Contd.)",
            "Adult Health Nursing 1 (Practical)",
            "Emirates Society",
            "Health Informatics & Technology",
        ],
        "Semester 5": [
            "Nursing Education",
            "Paediatric Nursing",
            "Psychiatric Mental Health Nursing",
            "Adult Health Nursing-2",
            "Nursing Leadership & Management",
            "Professional Issues & Trends in Nursing",
            "Legal & Ethical Issues in Nursing",
            "Gynecological Nursing",
        ],
        "Semester 6": [
            "Nursing Education (Contd.)",
            "Paediatric Nursing (Contd.)",
            "Psychiatric Mental Health Nursing (Contd.)",
            "Adult Health Nursing-2 (Contd.)",
            "Nursing Leadership & Management (Contd.)",
            "Professional Issues & Trends in Nursing (Contd.)",
            "Legal & Ethical Issues in Nursing (Contd.)",
        ],
        "Semester 7": [
            "Obstetric Nursing",
            "Critical Care Nursing",
            "Community Health Nursing",
            "Clinical Practicum",
        ],
        "Semester 8": [
            "Obstetric Nursing (Contd.)",
            "Critical Care Nursing (Contd.)",
            "Community Health Nursing (Contd.)",
            "Clinical Practicum Elective",
            "Nursing Research Methodology & Statistics",
        ],
    },
}

courses_credits = {
    "English": 3,
    "Health Sciences Communication in Arabic": 2,
    "Foundations of Nursing Practice-1": 3,
    "Foundations of Nursing Practice-1 (Practical)": 3,
    "Anatomy": 1.5,
    "Physiology": 1.5,
    "Nutrition & Dietetics": 2,
    "Health Sciences Communication in English": 2,
    "Microbiology": 3,
    "Foundations of Nursing Practice-2": 3,
    "Foundations of Nursing Practice-2 (Practical)": 2.5,
    "Anatomy (Contd.)": 1.5,
    "Physiology (Contd.)": 1.5,
    "Health Assessment": 1,
    "Health Assessment (Practical)": 3,
    "Pharmacology in Nursing": 1,
    "Human Biochemistry": 3,
    "Pathophysiology": 2,
    "Adult Health Nursing 1": 3,
    "Adult Health Nursing 1 (Practical)": 2.5,
    "Psychology": 2,
    "Pharmacology in Nursing (Contd.)": 2,
    "Islamic Culture & Medicine": 2,
    "Adult Health Nursing 1 (Contd.)": 2,
    "Adult Health Nursing 1 (Practical)": 2,
    "Emirates Society": 2,
    "Health Informatics & Technology": 3,
    "Nursing Education": 1,
    "Paediatric Nursing": 3.5,
    "Psychiatric Mental Health Nursing": 3,
    "Adult Health Nursing-2": 3.5,
    "Nursing Leadership & Management": 2,
    "Professional Issues & Trends in Nursing": 1,
    "Legal & Ethical Issues in Nursing": 1,
    "Gynecological Nursing": 2,
    "Nursing Education (Contd.)": 1.5,
    "Paediatric Nursing (Contd.)": 2.5,
    "Psychiatric Mental Health Nursing (Contd.)": 2,
    "Adult Health Nursing-2 (Contd.)": 4,
    "Nursing Leadership & Management (Contd.)": 1,
    "Professional Issues & Trends in Nursing (Contd.)": 1,
    "Legal & Ethical Issues in Nursing (Contd.)": 1,
    "Obstetric Nursing": 2.5,
    "Critical Care Nursing": 2,
    "Community Health Nursing": 1.5,
    "Clinical Practicum": 4,
    "Obstetric Nursing (Contd.)": 3,
    "Critical Care Nursing (Contd.)": 3,
    "Community Health Nursing (Contd.)": 2,
    "Clinical Practicum Elective": 3,
    "Nursing Research Methodology & Statistics": 3,
}

main_menu_keyboard = {
    "ar": [
        ["📊 حساب الانترنل"],
        ["🎯 حساب عدد أسئلة النجاح في الفاينل"],
        ["🎓 حساب المعدل (GPA)"],
        ["❌ خروج"],
    ],
    "en": [
        ["📊 Internal Calculator"],
        ["🎯 Calculate Required Final Exam Questions to Pass"],
        ["🎓 GPA Calculator"],
        ["❌ Exit"],
    ],
}

def parse_grade_input(text):
    text = text.strip()
    if '/' in text:
        try:
            got, total = text.split('/')
            got = float(got.strip())
            total = float(total.strip())
            if total == 0 or got < 0 or got > total:
                return None, "Invalid marks, please enter like 22/25."
            percent = (got / total) * 100
            return percent, None
        except Exception:
            return None, "Invalid format, please enter like 22/25."
    else:
        try:
            val = float(text)
            if val < 0 or val > 100:
                return None, "Score should be between 0 and 100."
            return val, None
        except Exception:
            return None, "Invalid input, please enter number or like 22/25."

def percent_to_gpa(percent):
    if percent >= 95:
        return 4.0
    elif percent >= 90:
        return 3.7
    elif percent >= 85:
        return 3.3
    elif percent >= 80:
        return 3.0
    elif percent >= 75:
        return 2.7
    elif percent >= 70:
        return 2.0
    elif percent >= 65:
        return 1.7
    elif percent >= 60:
        return 1.0
    else:
        return 0.0

async def start(update: Update, context: CallbackContext) -> int:
    reply_markup = ReplyKeyboardMarkup(
        [["العربية"], ["English"]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    await update.message.reply_text("اختر اللغة / Choose your language:", reply_markup=reply_markup)
    return LANGUAGE

async def language_selection(update: Update, context: CallbackContext) -> int:
    lang = update.message.text
    if lang == "العربية":
        context.user_data["lang"] = "ar"
    elif lang == "English":
        context.user_data["lang"] = "en"
    else:
        await update.message.reply_text("رجاءً اختر مباشرة من القائمة. / Please choose from the list.")
        return LANGUAGE

    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[context.user_data["lang"]], resize_keyboard=True)
    msg = "اختر خيارًا:" if context.user_data["lang"] == "ar" else "Please choose an option:"
    await update.message.reply_text(msg, reply_markup=reply_markup)
    return MAIN_MENU

async def main_menu(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    text = update.message.text

    if lang == "ar":
        if text == "📊 حساب الانترنل":
            reply_markup = ReplyKeyboardMarkup(
                [[sem] for sem in semesters["ar"].keys()] + [["⬅️ رجوع للقائمة"]],
                one_time_keyboard=True,
                resize_keyboard=True,
            )
            await update.message.reply_text("اختر السمستر:", reply_markup=reply_markup)
            return INTERNAL_SEMESTER

        elif text == "🎯 حساب عدد أسئلة النجاح في الفاينل":
            await update.message.reply_text("كم جبت في الانترنل؟ (مثال: 70)")
            return FINAL_INTERNAL_SCORE

        elif text == "🎓 حساب المعدل (GPA)":
            context.user_data["gpa_courses"] = []
            context.user_data["gpa_all_courses"] = []
            for sem in semesters["en"]:
                context.user_data["gpa_all_courses"].extend(semesters["en"][sem])
            context.user_data["gpa_index"] = 0
            return await ask_gpa_course_grade(update, context)

        elif text == "❌ خروج":
            await update.message.reply_text("شكرًا لاستخدامك البوت 😊", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        elif text == "⬅️ رجوع للقائمة":
            reply_markup = ReplyKeyboardMarkup(main_menu_keyboard["ar"], resize_keyboard=True)
            await update.message.reply_text("اختر خيارًا:", reply_markup=reply_markup)
            return MAIN_MENU

        else:
            await update.message.reply_text("يرجى اختيار خيار صالح من القائمة.")
            return MAIN_MENU

    else:
        if text == "📊 Internal Calculator":
            reply_markup = ReplyKeyboardMarkup(
                [[sem] for sem in semesters["en"].keys()] + [["⬅️ Back to Menu"]],
                one_time_keyboard=True,
                resize_keyboard=True,
            )
            await update.message.reply_text("Please choose the semester:", reply_markup=reply_markup)
            return INTERNAL_SEMESTER

        elif text == "🎯 Calculate Required Final Exam Questions to Pass":
            await update.message.reply_text("What was your internal score? (e.g. 70)")
            return FINAL_INTERNAL_SCORE

        elif text == "🎓 GPA Calculator":
            context.user_data["gpa_courses"] = []
            context.user_data["gpa_all_courses"] = []
            for sem in semesters["en"]:
                context.user_data["gpa_all_courses"].extend(semesters["en"][sem])
            context.user_data["gpa_index"] = 0
            return await ask_gpa_course_grade(update, context)

        elif text == "❌ Exit":
            await update.message.reply_text("Thank you for using the bot 😊", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        elif text == "⬅️ Back to Menu":
            reply_markup = ReplyKeyboardMarkup(main_menu_keyboard["en"], resize_keyboard=True)
            await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)
            return MAIN_MENU

        else:
            await update.message.reply_text("Please choose a valid option from the list.")
            return MAIN_MENU

async def internal_semester_selection(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    semester = update.message.text
    if semester == "⬅️ رجوع للقائمة" or semester == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU

    if semester not in semesters[lang]:
        await update.message.reply_text("رجاءً اختر السمستر من القائمة." if lang == "ar" else "Please choose a semester from the list.")
        return INTERNAL_SEMESTER

    context.user_data["semester"] = semester
    subjects = semesters[lang][semester]
    reply_markup = ReplyKeyboardMarkup(
        [[subj] for subj in subjects] + [["⬅️ رجوع للقائمة"] if lang == "ar" else ["⬅️ Back to Menu"]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    await update.message.reply_text("اختر المادة:" if lang == "ar" else "Please choose the subject:", reply_markup=reply_markup)
    return INTERNAL_SUBJECT

async def internal_subject_selection(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    semester = context.user_data["semester"]
    subject = update.message.text

    if subject == "⬅️ رجوع للقائمة" or subject == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU

    if subject not in semesters[lang][semester]:
        await update.message.reply_text("رجاءً اختر المادة من القائمة." if lang == "ar" else "Please choose a subject from the list.")
        return INTERNAL_SUBJECT
    context.user_data["subject"] = subject

    if lang == "ar":
        reply_markup = ReplyKeyboardMarkup([["فصلية"], ["سنوية"], ["⬅️ رجوع للقائمة"]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل المادة فصلية أم سنوية؟", reply_markup=reply_markup)
    else:
        reply_markup = ReplyKeyboardMarkup([["Semester"], ["Yearly"], ["⬅️ Back to Menu"]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Is the course Semester or Yearly?", reply_markup=reply_markup)
    return INTERNAL_COURSE_TYPE

async def internal_course_type_selection(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    ctype = update.message.text

    if ctype == "⬅️ رجوع للقائمة" or ctype == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU

    valid_ar = ["فصلية", "سنوية"]
    valid_en = ["Semester", "Yearly"]

    if (lang == "ar" and ctype not in valid_ar) or (lang == "en" and ctype not in valid_en):
        await update.message.reply_text('رجاءً اختر "فصلية" أو "سنوية".' if lang == "ar" else 'Please choose "Semester" or "Yearly".')
        return INTERNAL_COURSE_TYPE

    if lang == "en":
        ctype = "فصلية" if ctype == "Semester" else "سنوية"

    context.user_data["course_type"] = ctype
    context.user_data["grades"] = {}
    context.user_data["question_index"] = 0

    internal_questions_semester = {
        "ar": [
            ("CA1", "كم جبت في ال CA1؟ (مثال: 22/25)"),
            ("Quiz1", "كم جبت في ال Quiz 1؟ (مثال: 8/10)"),
            ("IRAT1", "كم جبت في ال IRAT 1؟ (مثال: 12/15)"),
            ("TRAT1", "كم جبت في ال TRAT 1؟ (مثال: 13/15)"),
            ("Assignment1", "كم جبت في ال Assignment 1؟ (مثال: 18/20)"),
        ],
        "en": [
            ("CA1", "What did you score in CA1? (e.g. 22/25)"),
            ("Quiz1", "What did you score in Quiz 1? (e.g. 8/10)"),
            ("IRAT1", "What did you score in IRAT 1? (e.g. 12/15)"),
            ("TRAT1", "What did you score in TRAT 1? (e.g. 13/15)"),
            ("Assignment1", "What did you score in Assignment 1? (e.g. 18/20)"),
        ],
    }

    internal_questions_semesterly = {
        "ar": [
            ("CA1", "كم جبت في ال CA1؟ (مثال: 22/25)"),
            ("CA2", "كم جبت في ال CA2؟ (مثال: 30/35)"),
            ("Quiz1", "كم جبت في ال Quiz 1؟ (مثال: 8/10)"),
            ("Quiz2", "كم جبت في ال Quiz 2؟ (مثال: 9/10)"),
            ("IRAT1", "كم جبت في ال IRAT 1؟ (مثال: 13/15)"),
            ("IRAT2", "كم جبت في ال IRAT 2؟ (مثال: 14/15)"),
            ("TRAT1", "كم جبت في ال TRAT 1؟ (مثال: 14/15)"),
            ("TRAT2", "كم جبت في ال TRAT 2؟ (مثال: 13/15)"),
            ("Assignment1", "كم جبت في ال Assignment 1؟ (مثال: 17/20)"),
            ("Assignment2", "كم جبت في ال Assignment 2؟ (مثال: 18/20)"),
        ],
        "en": [
            ("CA1", "What did you score in CA1? (e.g. 22/25)"),
            ("CA2", "What did you score in CA2? (e.g. 30/35)"),
            ("Quiz1", "What did you score in Quiz 1? (e.g. 8/10)"),
            ("Quiz2", "What did you score in Quiz 2? (e.g. 9/10)"),
            ("IRAT1", "What did you score in IRAT 1? (e.g. 13/15)"),
            ("IRAT2", "What did you score in IRAT 2? (e.g. 14/15)"),
            ("TRAT1", "What did you score in TRAT 1? (e.g. 14/15)"),
            ("TRAT2", "What did you score in TRAT 2? (e.g. 13/15)"),
            ("Assignment1", "What did you score in Assignment 1? (e.g. 17/20)"),
            ("Assignment2", "What did you score in Assignment 2? (e.g. 18/20)"),
        ],
    }

    if ctype == "فصلية":
        context.user_data["questions"] = internal_questions_semester[lang]
    else:
        context.user_data["questions"] = internal_questions_semesterly[lang]

    key, question = context.user_data["questions"][0]
    await update.message.reply_text(question, reply_markup=ReplyKeyboardRemove())
    return INTERNAL_GRADE_INPUT

async def internal_grade_input(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    text = update.message.text.strip()
    if text == "⬅️ رجوع للقائمة" or text == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU

    percent, error = parse_grade_input(text)
    if error:
        await update.message.reply_text(error)
        return INTERNAL_GRADE_INPUT

    idx = context.user_data["question_index"]
    key, _ = context.user_data["questions"][idx]
    context.user_data["grades"][key] = percent

    idx += 1
    if idx >= len(context.user_data["questions"]):
        total_internal = compute_final_internal(context.user_data["course_type"], context.user_data["grades"])
        subject = context.user_data["subject"]
        msg = ""
        if lang == "ar":
            msg = f"النتيجة النهائية للانترنل للمادة {subject} هي: {total_internal:.2f} من 100."
            msg += "\nالمادة فصلية." if context.user_data["course_type"] == "فصلية" else "\nالمادة سنوية."
            msg += "\n\nللبدء مجددًا ارسل /start"
        else:
            msg = f"Final internal score for course {subject} is: {total_internal:.2f} out of 100."
            msg += "\nThe course is Semester." if context.user_data["course_type"] == "فصلية" else "\nThe course is Yearly."
            msg += "\n\nTo start over, send /start"
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True))
        return MAIN_MENU
    else:
        context.user_data["question_index"] = idx
        _, question = context.user_data["questions"][idx]
        await update.message.reply_text(question)
        return INTERNAL_GRADE_INPUT

def compute_final_internal(course_type, grades):
    if course_type == "فصلية":
        ca = grades.get("CA1", 0)
        quiz = grades.get("Quiz1", 0)
        irat = grades.get("IRAT1", 0)
        trat = grades.get("TRAT1", 0)
        assignment = grades.get("Assignment1", 0)

        ca_score = ca * 0.50
        tbl_score = ((irat + trat) / 2) * 0.15
        quiz_score = quiz * 0.15
        assignment_score = assignment * 0.20

        return ca_score + tbl_score + quiz_score + assignment_score
    else:
        ca = (grades.get("CA1", 0) + grades.get("CA2", 0)) / 2
        quiz = (grades.get("Quiz1", 0) + grades.get("Quiz2", 0)) / 2
        irat = (grades.get("IRAT1", 0) + grades.get("IRAT2", 0)) / 2
        trat = (grades.get("TRAT1", 0) + grades.get("TRAT2", 0)) / 2
        assignment = (grades.get("Assignment1", 0) + grades.get("Assignment2", 0)) / 2

        ca_score = ca * 0.50
        tbl_score = ((irat + trat) / 2) * 0.15
        quiz_score = quiz * 0.15
        assignment_score = assignment * 0.20

        return ca_score + tbl_score + quiz_score + assignment_score

async def final_internal_score_input(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    text = update.message.text.strip()
    if text == "⬅️ رجوع للقائمة" or text == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU

    try:
        internal_score = float(text)
        if internal_score < 0 or internal_score > 100:
            raise ValueError
    except:
        msg = "يرجى إدخال درجة صحيحة بين 0 و 100." if lang == "ar" else "Please enter a valid score between 0 and 100."
        await update.message.reply_text(msg)
        return FINAL_INTERNAL_SCORE

    context.user_data["internal_score"] = internal_score
    msg = "كم عدد الأسئلة في الامتحان النهائي؟ (مثال: 75)" if lang == "ar" else "How many questions are in the final exam? (e.g. 75)"
    await update.message.reply_text(msg)
    return FINAL_TOTAL_QUESTIONS

async def final_total_questions_input(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    text = update.message.text.strip()
    if text == "⬅️ رجوع للقائمة" or text == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU
    try:
        total_questions = int(text)
        if total_questions <= 0:
            raise ValueError
    except:
        msg = "يرجى إدخال عدد صحيح أكبر من صفر." if lang == "ar" else "Please enter a valid integer greater than zero."
        await update.message.reply_text(msg)
        return FINAL_TOTAL_QUESTIONS

    context.user_data["total_questions"] = total_questions
    msg = "ما هي الدرجة النهائية التي تريد ان تحصل عليها؟ (مثال: 90)" if lang == "ar" else "What is the final grade you want to get? (e.g. 90)"
    await update.message.reply_text(msg)
    return FINAL_PASS_PERCENT

async def final_pass_percent_input(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    text = update.message.text.strip()
    if text == "⬅️ رجوع للقائمة" or text == "⬅️ Back to Menu":
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU
    try:
        passing_percent = float(text)
        if passing_percent < 0 or passing_percent > 100:
            raise ValueError
    except:
        msg = "يرجى إدخال نسبة صحيحة بين 0 و 100." if lang == "ar" else "Please enter a valid percentage between 0 and 100."
        await update.message.reply_text(msg)
        return FINAL_PASS_PERCENT

    internal_score = context.user_data["internal_score"]
    total_questions = context.user_data["total_questions"]

    final_needed_percent = (passing_percent - 0.6 * internal_score) / 0.4
    final_needed_percent = max(0, min(final_needed_percent, 100))
    questions_to_solve = round((final_needed_percent / 100) * total_questions)

    msg = ""
    if lang == "ar":
        msg = (
            f"بناءً على درجة الانترنل {internal_score:.2f}% وعدد الأسئلة {total_questions},\n"
            f"يجب عليك حل حوالي {questions_to_solve} سؤالًا على الأقل لتحصل على {passing_percent}%.\n"
            "للبدء مجددًا ارسل /start"
        )
    else:
        msg = (
            f"Based on your internal score {internal_score:.2f}% and total questions {total_questions},\n"
            f"you need to correctly answer about {questions_to_solve} questions to achieve {passing_percent}%.\n"
            "To start over, send /start"
        )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True))
    return MAIN_MENU

async def ask_gpa_course_grade(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    gpa_courses = []
    for sem in semesters["en"]:
        gpa_courses.extend(semesters["en"][sem])
    context.user_data["gpa_courses"] = gpa_courses
    context.user_data["gpa_grades"] = []
    context.user_data["gpa_index"] = 0
    return await gpa_ask_next(update, context)

async def gpa_ask_next(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    idx = context.user_data.get("gpa_index", 0)
    courses = context.user_data["gpa_courses"]

    if idx >= len(courses):
        return await gpa_show_result(update, context)

    course = courses[idx]
    context.user_data["current_gpa_course"] = course
    msg = f"Enter your grade for {course} (e.g. 3.5 or 85/100):"
    reply_markup = ReplyKeyboardMarkup([["Back to Menu"]] if lang == "en" else [["⬅️ رجوع للقائمة"]], resize_keyboard=True)
    await update.message.reply_text(msg, reply_markup=reply_markup)
    return GPA_GRADE_INPUT

async def gpa_grade_input(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    text = update.message.text.strip()

    if (lang == "ar" and text == "⬅️ رجوع للقائمة") or (lang == "en" and text.lower() == "back to menu"):
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True)
        await update.message.reply_text("اختر خيارًا:" if lang == "ar" else "Please choose an option:", reply_markup=reply_markup)
        return MAIN_MENU

    grade, err = parse_grade_input(text)
    if err:
        await update.message.reply_text(err)
        return GPA_GRADE_INPUT

    if grade > 4.0:
        grade = percent_to_gpa(grade)

    context.user_data["gpa_grades"].append((context.user_data["current_gpa_course"], grade))
    context.user_data["gpa_index"] += 1
    return await gpa_ask_next(update, context)

async def gpa_show_result(update: Update, context: CallbackContext) -> int:
    lang = context.user_data["lang"]
    grades = context.user_data.get("gpa_grades", [])

    if not grades:
        msg = "لم تدخل أي درجات لحساب المعدل." if lang == "ar" else "You did not enter any grades to calculate GPA."
        await update.message.reply_text(msg)
        return MAIN_MENU

    numerator = 0.0
    denominator = 0.0
    for course, grade in grades:
        credits = courses_credits.get(course, 3)
        numerator += grade * credits
        denominator += credits

    final_gpa = numerator / denominator if denominator != 0 else 0
    text = (
        f"حساب المعدل التراكمي (GPA) الخاص بك هو: {final_gpa:.2f}\nللبدء مجددًا ارسل /start"
        if lang == "ar"
        else f"Your cumulative GPA is: {final_gpa:.2f}\nTo start over, send /start"
    )
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(main_menu_keyboard[lang], resize_keyboard=True))
    return MAIN_MENU


async def cancel(update: Update, context: CallbackContext) -> int:
    lang = context.user_data.get("lang", "ar")
    msg = "تم إلغاء العملية." if lang == "ar" else "Operation cancelled."
    update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def main():
    application = ApplicationBuilder().token("7973621327:AAEnI2xrOlUJGvOhWEFTQMzd9vpdOQQQlvI").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_selection)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            INTERNAL_SEMESTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_semester_selection)],
            INTERNAL_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_subject_selection)],
            INTERNAL_COURSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_course_type_selection)],
            INTERNAL_GRADE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_grade_input)],
            FINAL_INTERNAL_SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, final_internal_score_input)],
            FINAL_TOTAL_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, final_total_questions_input)],
            FINAL_PASS_PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, final_pass_percent_input)],
            GPA_GRADE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpa_grade_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

   
    application.add_handler(conv_handler)
    await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
