import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import io
import base64
import matplotlib as mpl
import matplotlib.font_manager as fm

# הגדרת העמוד והסגנון
st.set_page_config(page_title="מחשבון חלוקת חשבון חשמל", layout="wide", initial_sidebar_state="expanded")

# הוספת CSS ליישור הדף לימין עבור תמיכה בעברית
st.markdown("""
<style>
    /* יישור כללי של האתר לימין */
    .main .block-container {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור כותרות לימין */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6, .main p {
        text-align: right;
    }
    
    /* יישור תוויות של קלט לימין */
    .stTextInput label, .stNumberInput label, .stDateInput label, .stTimeInput label, .stSelectbox label, .stMultiselect label {
        text-align: right;
        direction: rtl;
    }
    
    /* יישור תיבות טקסט לימין */
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input, div[data-baseweb="textarea"] textarea {
        text-align: right;
        direction: rtl;
    }
    
    /* יישור טקסט בתוך אזהרות ומידע */
    .stAlert div, .stInfo div {
        text-align: right;
        direction: rtl;
    }
    
    /* תיקון כיוון לסרגל הצד */
    .css-1d391kg, .css-1lcbmhc, .css-12oz5g7 {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור מטריקות */
    .stMetric label {
        text-align: right;
    }
    
    /* כפתורים ואלמנטי UI נוספים */
    .stButton, .stDownloadButton, .stFileUploader {
        text-align: right;
    }
    
    /* תיקון כיוון למרכיבים נוספים */
    .element-container, .stMarkdown, .stExpander {
        direction: rtl;
    }
    
    /* יישור תוכן של אקסלים וטבלאות */
    .dataframe {
        text-align: right;
        direction: rtl;
    }
    
    /* כותרות ללשוניות גם מיושרות לימין */
    .stTabs [role="tab"] {
        direction: rtl;
        text-align: right;
    }
    
    /* תיקון לרשימות */
    ul, ol {
        padding-right: 1rem;
        padding-left: 0;
    }
    
    /* טקסט במידע הסבר (tooltip) */
    .stTooltipIcon > span {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# עדכון CSS לטבלה עם מפריד אנכי ושינוי רקע בעמודות
st.markdown("""
<style>
    .dataframe { border-collapse: collapse; width: 100%; text-align: right !important; direction: rtl; }
    .dataframe th, .dataframe td { padding: 8px; border-bottom: 1px solid #dee2e6; position: relative; }
    .dataframe th { background-color: #f8f9fa; border-bottom: 2px solid #dee2e6; font-weight: bold; }
    /* מפריד אנכי לפני העמודה השנייה (לפי החשבונית ב-RTL) */
    .dataframe th:nth-child(2), .dataframe td:nth-child(2) {
        border-left: 2px solid #dee2e6;
        background-color: rgba(240, 248, 255, 0.3);
    }
    /* רקע קל לעמודה השלישית (לפי התמונות ב-RTL) */
    .dataframe th:nth-child(3), .dataframe td:nth-child(3) {
        background-color: rgba(248, 245, 240, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# הגדרת תמיכה לעברית במטפלוטליב
def setup_hebrew_fonts():
    # הגדרת פונט ברירת מחדל שתומך בעברית
    # ניסיון להשתמש בפונטים נפוצים שתומכים בעברית
    hebrew_fonts = ['Arial', 'David', 'Times New Roman', 'Noto Sans Hebrew', 'Segoe UI', 'DejaVu Sans']
    
    # לולאה שבודקת איזה פונט קיים במערכת
    font_found = False
    for font in hebrew_fonts:
        font_paths = [f.fname for f in fm.fontManager.ttflist if font.lower() in f.name.lower()]
        if font_paths:
            mpl.rcParams['font.family'] = font
            font_found = True
            break
    
    # הגדרת כיוון טקסט מימין לשמאל
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['font.size'] = 10

# קריאה לפונקציה להגדרת הפונטים
setup_hebrew_fonts()

# פונקציה לטיפול בטקסט עברי בגרפים
def fix_hebrew_text(text):
    # מהפך את סדר התווים בטקסט עברי כדי שיוצג נכון במטפלוטליב
    return text[::-1]

# פונקציה מותאמת להזנת תאריך בפורמט dd/mm/yyyy
def custom_date_input(label, key=None, value=None):
    if value is None:
        value = datetime.now()
    
    date_str = st.text_input(
        label,
        value=value.strftime("%d/%m/%Y"),
        key=key,
        help="פורמט: dd/mm/yyyy (לדוגמה: 25/12/2023)"
    )
    
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        st.error(f"פורמט תאריך שגוי. נא להזין במבנה dd/mm/yyyy (לדוגמה: 25/12/2023)")
        return value.date()

# פונקציה מותאמת להצגת מספרים עם פסיק מפריד אלפים
def format_meter_reading(number):
    if number is None or number == "":
        return ""
    try:
        # אם המספר הוא אפס, החזר מחרוזת ריקה
        if float(number) == 0:
            return ""
        return f"{float(number):,.1f}".replace(",", "פ").replace(".", ",").replace("פ", ".")
    except ValueError:
        return ""

def custom_number_input(label, key, min_value=0.0, value=0.0, help=None):
    # הצגת ערך נוכחי עם פסיק כמפריד אלפים, אבל רק אם הוא לא אפס
    formatted_value = format_meter_reading(value)
    
    # שימוש בטקסט להזנת המספר
    input_str = st.text_input(
        label,
        value=formatted_value,
        key=key,
        help=help
    )
    
    # הוספת JavaScript לפורמט אוטומטי של המספר בזמן הזנה והקלדה
    st.markdown(r"""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // חכה רגע לטעינת הממשק של Streamlit
            setTimeout(function() {
                // בחר את כל שדות הטקסט של Streamlit
                const textInputs = Array.from(document.querySelectorAll('input[type="text"]'));
                
                textInputs.forEach(input => {
                    // פורמט בזמן עזיבת השדה
                    input.addEventListener('blur', function() {
                        formatNumberWithThousandsSeparator(this);
                    });
                    
                    // פורמט בזמן הקלדה (אחרי שהמשתמש מקליד)
                    input.addEventListener('input', function() {
                        formatNumberWithThousandsSeparator(this);
                    });
                });
                
                function formatNumberWithThousandsSeparator(inputElement) {
                    let value = inputElement.value;
                    if (!value || value.trim() === '') return;
                    
                    // בדיקה האם הערך מכיל רק מספרים ונקודה/פסיק
                    if (!/^[\d.,]+$/.test(value.replace(/[^\d.,]/g, ''))) {
                        return;
                    }
                    
                    try:
                        const cursorPosition = inputElement.selectionStart;
                        const previousLength = value.length;
                        
                        let cleanValue = value.replace(/[^\d.,]/g, '');
                        cleanValue = cleanValue.replace(/,/g, '.');
                        
                        let parts = cleanValue.split('.');
                        if (parts.length > 2) {
                            cleanValue = parts[0] + '.' + parts.slice(1).join('');
                        }
                        
                        const numValue = parseFloat(cleanValue);
                        if (isNaN(numValue)) return;
                        
                        let formattedValue = numValue.toLocaleString('he-IL', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: (cleanValue.includes('.') ? 2 : 0)
                        });
                        
                        if (value !== formattedValue) {
                            inputElement.value = formattedValue;
                            const lengthDiff = formattedValue.length - previousLength;
                            const newPosition = cursorPosition + lengthDiff;
                            inputElement.setSelectionRange(newPosition, newPosition);
                        }
                    } catch (e) {
                        console.error("שגיאה בפורמט המספר:", e);
                    }
                }
            }, 1000);
        });
    </script>
    """, unsafe_allow_html=True)
    
    # המרה חזרה למספר
    try:
        if input_str:
            # תיקון: טיפול נכון בפסיק ונקודה עברית
            # הסרת פסיקים כמפרידי אלפים והמרת נקודה עשרונית
            clean_value = input_str
            
            # אם יש פסיק ונקודה - מניחים שהפסיק הוא מפריד אלפים והנקודה היא עשרונית
            if ',' in clean_value and '.' in clean_value:
                clean_value = clean_value.replace(',', '')
            # אם יש רק פסיק - מניחים שהוא הנקודה העשרונית
            elif ',' in clean_value:
                clean_value = clean_value.replace(',', '.')

            value = float(clean_value)
            if value < min_value:
                st.warning(f"הערך חייב להיות לפחות {min_value}")
                value = min_value
            return value
        return value
    except ValueError:
        st.error("אנא הזן מספר תקין")
        return value

# כותרת ראשית
st.title("מחשבון חלוקת חשבון חשמל")
st.markdown("מערכת לחלוקת חשבון חשמל בין שתי דיירות המשתמשות במונה משותף")
st.markdown("<p style='color: #00ab41; font-weight: bold; font-size: 22px; margin: 10px 0; padding: 8px; background-color: rgba(0,171,65,0.1); border-radius: 5px; text-align: center;'>במונים הקטנים השורה התחתונה קובעת</p>", unsafe_allow_html=True)

# הצגת דוגמה להזנת נתונים
st.info("""
**שים לב:** חובה להזין את קריאות המונה של שתי הדיירות כדי שהאפליקציה תוכל לחשב את חלוקת החשבון.
לדוגמה: אם הקריאה הקודמת של קרן היא 5000.0 והקריאה הנוכחית היא 5200.0, זה אומר שקרן צרכה 200 קוט"ש.
""")

# שדות תאריך משותפים
st.header(" תאריכי קריאות מונה מהתמונות ")
date_col1, date_col2 = st.columns(2)

with date_col2: # Changed from date_col1 to date_col2 to put it on the right
    # תאריך קריאה קודמת - משותף לשתי הדיירות
    shared_date_prev = custom_date_input("תאריך קריאה קודמת (משותף)", key="shared_date_prev")
    st.caption("תאריך זה משותף לקריאה הקודמת של קרן ועמית")

with date_col1: # Changed from date_col2 to date_col1 to put it on the left
    # תאריך קריאה נוכחית - משותף לשתי הדיירות
    shared_date_curr = custom_date_input("תאריך קריאה נוכחית (משותף)", key="shared_date_curr")  
    st.caption("תאריך זה משותף לקריאה הנוכחית של קרן ועמית")

# עדכון המשתנים הרלוונטיים לשימוש בהמשך הקוד
date_karen_prev = shared_date_prev
date_karen_curr = shared_date_curr
date_amit_prev = shared_date_prev
date_amit_curr = shared_date_curr

# נתוני קריאות מונה בשתי עמודות
col1, col2 = st.columns(2)

with col1:
    st.header("נתוני קריאת מונה - קרן")
    
    # קריאה קודמת
    st.subheader("קריאה קודמת")
    prev_reading_karen = custom_number_input(
        "קריאת מונה קודמת - קרן", 
        key="prev_karen", 
        min_value=0.0, 
        value=0.0,
        help="לדוגמה: 5,000.0"
    )
    
    # קריאה נוכחית
    st.subheader("קריאה נוכחית")
    curr_reading_karen = custom_number_input(
        "קריאת מונה נוכחית - קרן", 
        key="curr_karen", 
        min_value=0.0, 
        value=0.0,
        help="לדוגמה: 5,200.0 (חייב להיות גדול מהקריאה הקודמת)"
    )
    
    # חישוב צריכה
    karen_consumption = curr_reading_karen - prev_reading_karen
    if karen_consumption <= 0:
        st.warning("שים לב: הקריאה הנוכחית חייבת להיות גדולה מהקריאה הקודמת")
        karen_consumption = 0
    st.info(f"צריכת קרן: {karen_consumption:.1f} קוט\"ש")
    st.caption(f"החישוב: {curr_reading_karen:.1f} - {prev_reading_karen:.1f} = {karen_consumption:.1f} קוט\"ש")

with col2:
    st.header("נתוני קריאת מונה - עמית")
    
    # קריאה קודמת
    st.subheader("קריאה קודמת")
    prev_reading_amit = custom_number_input(
        "קריאת מונה קודמת - עמית", 
        key="prev_amit", 
        min_value=0.0, 
        value=0.0,
        help="לדוגמה: 3,000.0"
    )
    
    # קריאה נוכחית
    st.subheader("קריאה נוכחית")
    curr_reading_amit = custom_number_input(
        "קריאת מונה נוכחית - עמית", 
        key="curr_amit", 
        min_value=0.0, 
        value=0.0,
        help="לדוגמה: 3,150.0 (חייב להיות גדול מהקריאה הקודמת)"
    )
    
    # חישוב צריכה
    amit_consumption = curr_reading_amit - prev_reading_amit
    if amit_consumption <= 0:
        st.warning("שים לב: הקריאה הנוכחית חייבת להיות גדולה מהקריאה הקודמת")
        amit_consumption = 0
    st.info(f"צריכת עמית: {amit_consumption:.1f} קוט\"ש")
    st.caption(f"החישוב: {curr_reading_amit:.1f} - {prev_reading_amit:.1f} = {amit_consumption:.1f} קוט\"ש")

# חישוב צריכה כוללת
total_consumption = karen_consumption + amit_consumption

# הוספת שדות תאריכים ומידע על צריכה - שינוי לפי הדרישה החדשה
st.header("תקופת החשבון ונתוני צריכה מהחשבונית:")

# תאריכי חשבון - סדר חדש
st.subheader("תאריכי החשבון")

# הפוך את סדר העמודות כך שמתאריך יהיה בימין ועד תאריך בשמאל
date_col1, date_col2 = st.columns(2)
with date_col2:  # Changed from date_col1 to date_col2 to put it on the right
    bill_date_from = custom_date_input("מתאריך", key="bill_date_from")
with date_col1:  # Changed from date_col2 to date_col1 to put it on the left
    bill_date_to = custom_date_input("עד תאריך", key="bill_date_to")

# שדה לצריכה כוללת מהחשבונית - נשאר כפי שהיה
total_consumption_bill = st.number_input("סה\"כ צריכה מהחשבונית (קוט\"ש)", 
                                         min_value=0.0, 
                                         format="%.1f",
                                         help="הזן את סך הצריכה כפי שמופיע בחשבונית החשמל")

# חישוב הפרש בין הצריכות
consumption_diff = total_consumption_bill - total_consumption
diff_percentage = (abs(consumption_diff) / total_consumption_bill * 100) if total_consumption_bill > 0 else 0

# חישוב מספר ימים בין התאריכים מהתמונות
meters_days = (shared_date_curr - shared_date_prev).days if shared_date_curr and shared_date_prev else 0
# חישוב מספר ימים בין התאריכים מהחשבונית
bill_days = (bill_date_to - bill_date_from).days if bill_date_to and bill_date_from else 0

# חישוב ממוצע צריכה ליום
meters_avg_daily = total_consumption / meters_days if meters_days > 0 else 0
bill_avg_daily = total_consumption_bill / bill_days if bill_days > 0 else 0

# הצגת מידע על הצריכה המשותפת בטבלה
st.markdown("**נתוני הצריכה המחושבים:**")

# יצירת טבלה להשוואת נתוני צריכה עם המרת סדר העמודות
consumption_data = {
    "נתון": ["סה\"כ צריכה", "סה\"כ ימים", "ממוצע צריכה ליום"],
    "לפי החשבונית": [
        f"{total_consumption_bill:.1f} קוט\"ש",
        f"{bill_days} ימים",
        f"{bill_avg_daily:.2f} קוט\"ש"
    ],
    "לפי התמונות": [
        f"{total_consumption:.1f} קוט\"ש",
        f"{meters_days} ימים",
        f"{meters_avg_daily:.2f} קוט\"ש"
    ]
}
consumption_df = pd.DataFrame(consumption_data)

# הצגת הטבלה כ-HTML כדי לאפשר את הסגנון המותאם
html_table = consumption_df.to_html(index=False)
st.markdown(html_table, unsafe_allow_html=True)

# הצגת פירוט הצריכה של הדיירות עם שתי ספרות אחרי הנקודה באחוזים
st.info(f"""
* צריכת קרן: {karen_consumption:.1f} קוט\"ש ({(karen_consumption/total_consumption*100 if total_consumption > 0 else 0):.2f}%)
* צריכת עמית: {amit_consumption:.1f} קוט\"ש ({(amit_consumption/total_consumption*100 if total_consumption > 0 else 0):.2f}%)
""")

# הצגת הפרש בשורה נפרדת
if total_consumption_bill > 0:
    # בחירת צבע בהתאם לגודל ההפרש
    if abs(diff_percentage) < 2:
        diff_color = "#00ab41"  # ירוק
        diff_icon = "✓"
    elif abs(diff_percentage) < 5:
        diff_color = "#FFA500"  # כתום
        diff_icon = "⚠️"
    else:
        diff_color = "#FF0000"  # אדום
        diff_icon = "❗"

    st.markdown(f"""
    <div style="padding: 10px; border-radius: 5px; background-color: rgba(0, 0, 0, 0.05); margin-bottom: 20px;">
        <p style="color: {diff_color}; font-weight: bold; margin: 0;">
            {diff_icon} הפרש בין הצריכות(תמונות/חשבונית): {consumption_diff:.1f} קוט"ש ({diff_percentage:.1f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

# סעיף חשבון החשמל
st.header("נתוני חשבון החשמל")
uploaded_bill = st.file_uploader("העלאת חשבון החשמל (אופציונלי)", type=["pdf", "jpg", "png"])

# סעיף פירוט חיובים משותפים
st.header("פירוט חיובים משותפים")
col1, col2 = st.columns(2)
with col1:
    st.subheader("חיובים לפי צריכה משותפת")
    consumption_charge = st.number_input("חיוב בגין צריכה משותפת (₪)", min_value=0.0, format="%.2f", 
                                        help="הסכום המופיע בחשבון עבור צריכת חשמל בקוט\"ש")    
with col2:
    st.subheader("חיובים קבועים משותפים")
    # שינוי סדר השדות לפי הדרישה
    capacity_charges = st.number_input("תשלום משותף בגין הספק (KVA) (₪)", min_value=0.0, format="%.2f", 
                                     help="התשלום עבור ההספק המירבי")
    fixed_charges = st.number_input("תשלום משותף קבוע (₪)", min_value=0.0, format="%.2f", 
                                  help="התשלום הקבוע המופיע בחשבון")
    other_charges = st.number_input("חיובים וזיכויים שונים משותפים (₪)", min_value=-1000.0, value=0.0, format="%.2f", 
                                  help="חיובים וזיכויים נוספים המופיעים בחשבון")

# חישוב סך הכל חיובים
total_fixed_charges = fixed_charges + capacity_charges + other_charges
subtotal_before_vat = consumption_charge + total_fixed_charges

# חישוב מע"מ
vat_rate = st.number_input("שיעור המע\"מ (%)", min_value=0.0, max_value=100.0, value=18.0, format="%.1f") / 100
vat_amount = subtotal_before_vat * vat_rate

# סך הכל לתשלום
calculated_total = subtotal_before_vat + vat_amount

# הצגת סיכום החשבון בצורה ברורה
st.subheader("סיכום חשבון")
col_summary1, col_summary2 = st.columns(2)
with col_summary1:
    st.metric("סה\"כ ללא מע\"מ", f"{subtotal_before_vat:.2f} ₪")
    st.metric(f"מע\"מ ({vat_rate*100:.1f}%)", f"{vat_amount:.2f} ₪")
with col_summary2:
    st.metric("תשלום  כולל מע'מ ", f"{calculated_total:.2f} ₪", delta="סה\"כ לתשלום")

# חישוב חלוקת התשלום
if total_consumption > 0:
    karen_ratio = karen_consumption / total_consumption
    amit_ratio = amit_consumption / total_consumption
    
    # חישוב החלק היחסי של חיובי הצריכה
    karen_consumption_charge = consumption_charge * karen_ratio
    amit_consumption_charge = consumption_charge * amit_ratio
    
    # חלוקת החיובים הקבועים באופן שווה
    karen_fixed_charges = total_fixed_charges / 2
    amit_fixed_charges = total_fixed_charges / 2
    
    # חלוקת המע"מ
    karen_vat = (karen_consumption_charge + karen_fixed_charges) * vat_rate
    amit_vat = (amit_consumption_charge + amit_fixed_charges) * vat_rate
    
    # סך הכל לתשלום לכל דיירת
    karen_payment = karen_consumption_charge + karen_fixed_charges + karen_vat
    amit_payment = amit_consumption_charge + amit_fixed_charges + amit_vat
    
    # הצגת תוצאות
    st.header("תוצאות חלוקת החשבון")
    
    # ליצור שתי עמודות חדשות
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        st.subheader("קרן")
        st.metric("צריכה", f"{karen_consumption:.1f} קוט\"ש", f"{karen_ratio:.2%} מהצריכה")
        st.metric("חיוב בגין צריכה", f"{karen_consumption_charge:.2f} ₪")
        st.metric("חיובים קבועים", f"{karen_fixed_charges:.2f} ₪")
        st.metric("מע\"מ", f"{karen_vat:.2f} ₪")
        st.metric("סה\"כ לתשלום", f"{karen_payment:.2f} ₪", delta=f"{karen_payment/(karen_payment+amit_payment)*100:.2f}% מהחשבון")
    
    with result_col2:
        st.subheader("עמית")
        st.metric("צריכה", f"{amit_consumption:.1f} קוט\"ש", f"{amit_ratio:.2%} מהצריכה")
        st.metric("חיוב בגין צריכה", f"{amit_consumption_charge:.2f} ₪")
        st.metric("חיובים קבועים", f"{amit_fixed_charges:.2f} ₪")
        st.metric("מע\"מ", f"{amit_vat:.2f} ₪")
        st.metric("סה\"כ לתשלום", f"{amit_payment:.2f} ₪", delta=f"{amit_payment/(karen_payment+amit_payment)*100:.2f}% מהחשבון")
    
    # גרף התפלגות הצריכה
    st.subheader("התפלגות צריכת החשמל")
    
    # וודא שאין ערכים שליליים עבור גרף העוגה
    display_karen_consumption = max(karen_consumption, 0)
    display_amit_consumption = max(amit_consumption, 0)
    
    if display_karen_consumption > 0 or display_amit_consumption > 0:
        # הגדלת גובה הגרף כדי למנוע חיתוך של המספרים בראש העמודות
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # הגדלת הגובה מ-4 ל-5
        
        # גרף עוגה - התפלגות הצריכה
        # פתרון בעיית היפוך השמות - שימוש בפונקצית ההיפוך על שמות התוויות
        labels_orig = ['קרן', 'עמית']  # השמות המקוריים
        labels_fixed = [fix_hebrew_text(label) for label in labels_orig]  # היפוך השמות לתצוגה נכונה
        
        ax1.pie([display_karen_consumption, display_amit_consumption], 
                labels=labels_fixed,  # שימוש בשמות המתוקנים
                autopct='%1.2f%%',
                startangle=90,
                colors=['#ff9999', '#66b3ff'])
        ax1.set_title(fix_hebrew_text('התפלגות צריכת החשמל'), loc='center')
        
        # גרף עמודות - צריכה בקוט"ש - גם כאן צריך להפוך את השמות
        bars = ax2.bar(labels_fixed, [display_karen_consumption, display_amit_consumption], color=['#ff9999', '#66b3ff'])
        ax2.set_title(fix_hebrew_text('צריכת חשמל בקוט"ש'))
        ax2.set_ylabel(fix_hebrew_text('קוט"ש'))
        
        # הוספת ערכים מעל העמודות
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # נקודת הטקסט 3 נקודות מעל העמודה
                        textcoords="offset points",
                        ha='center', va='bottom')

        # הגדלת גבול הציר האנכי כדי לאפשר מקום למספרים מעל העמודות
        y_max = max(display_karen_consumption, display_amit_consumption)
        ax2.set_ylim(0, y_max * 1.1)  # תוספת של 10% לגובה המקסימלי
        
        plt.tight_layout(pad=1.5)  # הגדלת הריפוד מסביב לגרפים
        # יישור גרפים לכיוון RTL
        plt.rcParams['axes.titlepad'] = 14  # מרווח לכותרת
        plt.rcParams['figure.autolayout'] = True  # פריסה אוטומטית

        # מרווח נוסף להצגה נכונה של עברית
        fig.subplots_adjust(wspace=0.3)

        st.pyplot(fig)
    else:
        st.warning("לא ניתן להציג את גרפי התפלגות הצריכה כאשר אין צריכה חיובית.")

    # תיעוד היסטורי
    st.header("שמירת התיעוד")

    # יצירת קובץ CSV להורדה
    def get_csv():
        # שורת הכותרת והמוטו שיופיעו בראש הקובץ
        header_data = {
            'כותרת': ['מחשבון חלוקת חשבון חשמל', 'מערכת לחלוקת חשבון חשמל בין שתי דיירות', '']
        }
        header_df = pd.DataFrame(header_data)
        
        # מידע על תקופת החשבון
        bill_period_data = {
            'תקופת החשבון': [f'מתאריך: {bill_date_from.strftime("%d/%m/%Y")}', 
                            f'עד תאריך: {bill_date_to.strftime("%d/%m/%Y")}',
                            f'סה"כ צריכה מהחשבונית: {total_consumption_bill:.1f} קוט"ש',
                            f'סה"כ צריכה מחושבת: {total_consumption:.1f} קוט"ש',
                            f'הפרש: {consumption_diff:.1f} קוט"ש ({diff_percentage:.1f}%)']
        }
        bill_period_df = pd.DataFrame(bill_period_data)
        
        # הנתונים הרגילים
        data = {
            'פרמטר': [
                'תאריך קריאה קודמת', 
                'תאריך קריאה נוכחית', 
                'קריאת מונה קודמת', 
                'קריאת מונה נוכחית', 
                'צריכה (קוט"ש)', 
                'אחוז מהצריכה', 
                'חיוב בגין צריכה (₪)', 
                '(ספק,קבוע,חיוב/זיכוי)חיובים קבועים (₪)', 
                'מע"מ (₪)', 
                'סך הכל לתשלום (₪)'
            ],
            'קרן': [
                date_karen_prev.strftime("%d/%m/%Y"), 
                date_karen_curr.strftime("%d/%m/%Y"), 
                prev_reading_karen, 
                curr_reading_karen, 
                karen_consumption, 
                f"{karen_ratio:.2%}", 
                f"{karen_consumption_charge:.2f}", 
                f"{karen_fixed_charges:.2f}", 
                f"{karen_vat:.2f}", 
                f"{karen_payment:.2f}"
            ],
            'עמית': [
                date_amit_prev.strftime("%d/%m/%Y"), 
                date_amit_curr.strftime("%d/%m/%Y"), 
                prev_reading_amit, 
                curr_reading_amit, 
                amit_consumption, 
                f"{amit_ratio:.2%}", 
                f"{amit_consumption_charge:.2f}", 
                f"{amit_fixed_charges:.2f}", 
                f"{amit_vat:.2f}", 
                f"{amit_payment:.2f}"
            ]
        }
        
        # הוספת שורת סיכום של החשבון המקורי 
        summary_data = {
            'פרמטר': [
                'סך הכל חיוב בגין צריכה (₪)', 
                'סך הכל חיובים קבועים (₪)',
                'סך הכל לפני מע"מ (₪)',
                f'מע"מ בשיעור {vat_rate*100:.1f}% (₪)',
                'סך הכל כולל מע"מ (₪)'
            ],
            'נתוני חשבון': [
                f"{consumption_charge:.2f}",
                f"{total_fixed_charges:.2f}",
                f"{subtotal_before_vat:.2f}",
                f"{vat_amount:.2f}",
                f"{calculated_total:.2f}" 
            ],
            'הערות': [
                'מחולק לפי יחס צריכה',
                'מחולק שווה בשווה',
                '',
                '',
                ''
            ]
        }
        
        df = pd.DataFrame(data)
        df_summary = pd.DataFrame(summary_data)
        
        # יצירת CSV עם כל החלקים
        csv_output = header_df.to_csv(index=False)
        csv_output += "\n"  # שורה ריקה נוספת להפרדה
        csv_output += bill_period_df.to_csv(index=False)  # הוספת נתוני תקופת החשבון
        csv_output += "\n"  # שורה ריקה נוספת להפרדה
        csv_output += df.to_csv(index=False)
        csv_output += "\n\n"  # שתי שורות ריקות להפרדה
        csv_output += df_summary.to_csv(index=False)
        
        return csv_output.encode('utf-8')

    csv = get_csv()

    # יצירת לינק להורדת הקובץ
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="חלוקת_חשבון_חשמל.csv">לחץ כאן להורדת קובץ CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    if calculated_total > 0:
        st.warning("""
        **לא ניתן לחשב את חלוקת החשבון!**
        כדי שהמערכת תוכל לחשב את חלוקת החשבון, יש לוודא:
        1. שהזנת את קריאות המונה הקודמות והנוכחיות של שתי הדיירות
        2. שהקריאה הנוכחית גדולה מהקריאה הקודמת אצל שתי הדיירות
        3. שהצריכה הכוללת גדולה מ-0
        
        לדוגמה:
        - קריאה קודמת של קרן: 5000.0
        - קריאה נוכחית של קרן: 5200.0
        - קריאה קודמת של עמית: 3000.0
        - קריאה נוכחית של עמית: 3150.0
        - סכום החשבון המשותף: 500 ₪
        """)
    else:
        st.warning("נא להזין את קריאות המונה ופרטי החשבון כדי לחשב את חלוקת החשבון")

# מידע נוסף
with st.expander("מידע נוסף על אופן החישוב"):
    st.markdown("""
    **שיטת החישוב:**
    1. חישוב צריכת החשמל של כל דיירת בנפרד: קריאה נוכחית פחות קריאה קודמת.
    2. חישוב הצריכה הכוללת: סכום הצריכות של שתי הדיירות.
    3. חישוב האחוז היחסי מהצריכה הכוללת עבור כל דיירת.
    4. **חלוקת חיובים לפי צריכה**: החיוב בגין צריכה מחולק לפי יחס הצריכה של כל דיירת.
    5. **חלוקת חיובים קבועים**: התשלום הקבוע, תשלום בגין הספק, וחיובים שונים מחולקים שווה בשווה בין הדיירות.
    6. **חישוב מע"מ**: המע"מ מחושב על החיובים לאחר החלוקה (הן חיובי הצריכה והן החיובים הקבועים).
    
    **דוגמה למחשת החישוב:**
    - נניח שקרן צרכה 600 קוט"ש (60% מהצריכה) ועמית צרכה 400 קוט"ש (40% מהצריכה).
    - חיוב בגין צריכה: 740.53 ₪
    - חלק קרן: 740.53 * 60% = 444.32 ₪
    - חלק עמית: 740.53 * 40% = 296.21 ₪
    - חיובים קבועים: תשלום קבוע (43.05 ₪) + תשלום בגין הספק (3.48 ₪) + חיובים שונים (0.23 ₪) = 46.76 ₪
    - חלק קרן: 46.76 / 2 = 23.38 ₪
    - חלק עמית: 46.76 / 2 = 23.38 ₪
    - סה"כ לפני מע"מ:
    - קרן: 444.32 + 23.38 = 467.70 ₪
    - עמית: 296.21 + 23.38 = 319.59 ₪
    - מע"מ (17%):
    - קרן: 467.70 * 17% = 79.51 ₪
    - עמית: 319.59 * 17% = 54.33 ₪
    - סך הכל לתשלום:
    - קרן: 467.70 + 79.51 = 547.21 ₪
    - עמית: 319.59 + 54.33 = 373.92 ₪
    """)
    