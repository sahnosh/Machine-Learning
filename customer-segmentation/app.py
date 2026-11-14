from pathlib import Path
from datetime import date
import json
import altair as alt
import pandas as pd
import streamlit as st
from segmentation import read_orders, build_rfm, segment, csv_bytes

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Customer studio | دسته‌بندی مشتریان", page_icon=":material/group_work:", layout="wide")
st.caption("CUSTOMER STUDIO  /  RFM EXPLORER")
st.title("مشتریان خود را بهتر بشناسید")
st.markdown("رفتار خرید را به گروه‌های قابل‌فهم تبدیل کنید؛ از دادهٔ نمونه شروع کنید یا سفارش‌های خود را بارگذاری کنید.")

@st.cache_data(ttl=3600, max_entries=8, show_spinner=False)
def analyze(content, k, reference):
    orders, cleaning = read_orders(content)
    rfm, ref = build_rfm(orders, reference)
    customers, summary, metrics = segment(rfm, k)
    return customers, summary, metrics, cleaning, ref.date().isoformat()

with st.sidebar:
    st.header("تنظیم تحلیل")
    source = st.radio("منبع داده", ["دادهٔ نمونه", "بارگذاری CSV"], key="source")
    content = (ROOT / "sample_orders.csv").read_bytes()
    if source == "بارگذاری CSV":
        uploaded = st.file_uploader("فایل سفارش‌ها", type=["csv"], key="upload")
        st.caption("هر سطر یک سفارش؛ حداکثر ۱۰ مگابایت و ۱۰۰٬۰۰۰ سطر.")
        if uploaded is None:
            st.info("فایل CSV را انتخاب کنید تا تحلیل شروع شود.")
            st.download_button("دانلود الگوی CSV", content, "sample_orders.csv", "text/csv", key="template", width="stretch")
            st.code("customer_id,order_id,order_date,amount\nC001,O001,2026-10-20,125.50", language="text")
            st.stop()
        content = uploaded.getvalue()
    with st.form("settings"):
        groups = st.slider("تعداد گروه‌ها", 2, 8, 4, key="groups")
        use_date = st.checkbox("تاریخ مرجع دلخواه", key="use_date")
        reference = st.date_input("تاریخ مرجع", value=date(2026, 11, 1), key="reference")
        st.form_submit_button("اجرای تحلیل", type="primary", width="stretch", key="analyze")
    st.caption("پیش‌فرض: یک روز پس از آخرین خرید. برای اعمال تنظیمات، اجرای تحلیل را بزنید.")
    st.divider()
    st.markdown("**سه ویژگی رفتار خرید**")
    st.caption("Recency: روزهای گذشته از آخرین خرید\n\nFrequency: تعداد سفارش‌ها\n\nMonetary: مجموع مبلغ خرید")

if source == "دادهٔ نمونه":
    st.info("دادهٔ نمایشی مصنوعی: ۴۰۰ مشتری فرضی. این نتایج مربوط به یک کسب‌وکار واقعی نیستند.", icon=":material/science:")
try:
    with st.spinner("در حال تحلیل رفتار مشتریان…"):
        customers, summary, metrics, cleaning, ref = analyze(content, groups, str(reference) if use_date else None)
except ValueError as exc:
    st.error(str(exc), title="داده یا تنظیمات نیاز به اصلاح دارد")
    st.caption("ستون‌های لازم: customer_id، order_id، order_date، amount. تاریخ‌ها به صورت YYYY-MM-DD و مبلغ‌ها عدد مثبت باشند.")
    st.stop()

with st.container(horizontal=True):
    st.metric("مشتریان", f"{len(customers):,}", border=True)
    st.metric("سفارش‌های معتبر", f"{cleaning['valid_orders']:,}", border=True)
    st.metric("مجموع خرید", f"{customers.Monetary.sum():,.0f}", border=True)
    st.metric("تعداد گروه‌ها", str(groups), border=True)
st.caption(f"تاریخ مرجع: {ref}  ·  مبلغ‌ها در واحد پول فایل ورودی هستند.")
if cleaning["invalid_rows"] or cleaning["duplicate_rows"]:
    st.warning(f"سطرهای نامعتبر حذف‌شده: {cleaning['invalid_rows']}؛ سطرهای کاملاً تکراری حذف‌شده: {cleaning['duplicate_rows']}.")

view = st.segmented_control("نمایش", ["نمای کلی", "فهرست مشتریان", "روش و کیفیت"], default="نمای کلی", key="view")
if view == "نمای کلی":
    left, right = st.columns([2, 1])
    with left, st.container(border=True):
        st.subheader("نقشهٔ رفتار خرید")
        st.caption("هر نقطه یک مشتری است؛ اندازهٔ نقطه تعداد سفارش‌ها را نشان می‌دهد.")
        plotted = customers.sample(min(3000, len(customers)), random_state=42)
        scatter = alt.Chart(plotted, mark=alt.MarkDef(type="circle", opacity=.75)).encode(
            x=alt.X("Recency:Q", title="Days since last purchase"),
            y=alt.Y("Monetary:Q", title="Total spend (log scale)", scale=alt.Scale(type="log")),
            size=alt.Size("Frequency:Q", title="Orders", scale=alt.Scale(range=[30, 260])),
            color=alt.Color("Segment:N", sort=sorted(summary.Segment)),
            tooltip=["customer_id:N", "Segment:N", "Recency:Q", "Frequency:Q", alt.Tooltip("Monetary:Q", format=",.2f")],
        ).properties(height=350).interactive()
        st.altair_chart(scatter, alt="Customer spending and recency grouped by cluster")
        if len(customers) > 3000:
            st.caption("نمودار نمونه‌ای ثابت از ۳۰۰۰ مشتری را نشان می‌دهد؛ تحلیل شامل همهٔ مشتریان است.")
    with right, st.container(border=True):
        st.subheader("اندازهٔ گروه‌ها")
        bars = alt.Chart(summary, mark=alt.MarkDef(type="bar", cornerRadiusEnd=5)).encode(x=alt.X("Customers:Q", title="Customers"), y=alt.Y("Segment:N", title=None), color=alt.Color("Segment:N", legend=None), tooltip=["Segment:N", "Customers:Q", "Share (%):Q"]).properties(height=350)
        st.altair_chart(bars, alt="Number of customers in each segment")
    st.subheader("ویژگی هر گروه")
    st.caption("تازگی، تعداد سفارش و مبلغ خرید در این جدول میانه‌اند. توصیف‌ها نسبت به میانهٔ کل مشتریان‌اند؛ برچسب قطعی وفاداری نیستند.")
    st.dataframe(summary.round(2), hide_index=True, alt="Segment sizes, median RFM features, and descriptive profiles")
elif view == "فهرست مشتریان":
    selected = st.multiselect("انتخاب گروه", sorted(summary.Segment), default=sorted(summary.Segment), key="segments")
    query = st.text_input("جست‌وجوی شناسهٔ مشتری", key="search")
    visible = customers[customers.Segment.isin(selected)]
    if query:
        visible = visible[visible.customer_id.str.contains(query, case=False, regex=False)]
    st.caption(f"{len(visible):,} مشتری مطابق فیلتر")
    st.dataframe(visible.round(2), hide_index=True, alt="Customer-level RFM values and segment assignments")
    st.download_button("دانلود مشتریان فیلترشده", csv_bytes(visible), "filtered_customers.csv", "text/csv", key="filtered_download")
else:
    score = metrics["silhouette"]
    st.metric("Silhouette score", f"{score:.3f}" if score is not None else "N/A")
    st.caption(f"محاسبه روی {metrics['silhouette_sample']} مشتری؛ بازهٔ امتیاز از ۱− تا ۱ است. مقدار بالاتر معمولاً جدایی بیشتر گروه‌ها را نشان می‌دهد و دقت پیش‌بینی نیست.")
    st.markdown("۱. سفارش‌های نامعتبر و تکراری پاک می‌شوند.\n\n۲. برای هر مشتری سه ویژگی RFM ساخته می‌شود.\n\n۳. تبدیل log1p و استانداردسازی، تفاوت مقیاس‌ها را کاهش می‌دهد.\n\n۴. K-Means با مقداردهی K-Means++، ده شروع و بذر ثابت ۴۲ اجرا می‌شود.\n\n۵. گروه‌ها با رفتار واقعی‌شان تفسیر می‌شوند.")
    st.info("تعداد گروه‌ها را مقایسه کنید و هم‌زمان اندازه و معنای گروه‌ها را بررسی کنید. دادهٔ واقعی ممکن است گروه‌های مشخصی نداشته باشد.")
    st.caption("فقط سفارش‌های مثبت بررسی می‌شوند؛ بازپرداخت‌ها در این مدل از خریدها کسر نمی‌شوند. هر فایل باید یک واحد پول داشته باشد. گروه‌ها در اجرای جدید ممکن است تغییر کنند.")

st.divider()
with st.container(horizontal=True):
    st.download_button("دانلود همهٔ مشتریان", csv_bytes(customers), "customer_segments.csv", "text/csv", key="all_download", icon=":material/download:")
    st.download_button("دانلود خلاصهٔ گروه‌ها", csv_bytes(summary), "segment_summary.csv", "text/csv", key="summary_download")
    report = dict(metrics, cleaning=cleaning, reference_date=ref, source="synthetic_demo" if source == "دادهٔ نمونه" else "uploaded_csv")
    st.download_button("دانلود گزارش تحلیل", json.dumps(report, indent=2), "analysis_report.json", "application/json", key="report_download")
