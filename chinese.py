import streamlit as st
import pandas as pd
import re
import uuid

st.set_page_config(page_title="Chinese Words Dictionary", layout="wide")
st.sidebar.title("Chinese Dictionary")

@st.cache_data

def load_data():
    df = pd.read_excel("HelloChinese Word List_edited_2025.xlsx", sheet_name="HelloChinese")
    df = df.dropna(subset=["Characters / Traditional", "Pinyin", "Meaning"])
    df["Tags"] = df["Meaning"].apply(lambda m: re.findall(r"\b[A-Z]{1,4}\.", str(m)))

    # Add category mapping
    dimension_to_category = {
        "Hello": "Introductions",
        "Learning Chinese 1": "Language Learning",
        "Learning Chinese 2": "Language Learning",
        "School": "Language Learning",
        "Food": "Food & Dining",
        "Taste": "Food & Dining",
        "Ordering Food": "Food & Dining",
        "Restaurants 1": "Food & Dining",
        "Restaurants 2": "Food & Dining",
        "Helping Out": "Social Interactions",
        "Suggestions": "Social Interactions",
        "Dating": "Social Interactions",
        "Feelings": "Social Interactions",
        "Greetings": "Social Interactions",
        "Apologizing": "Social Interactions",
        "Gossip": "Social Interactions",
        "Arguments": "Social Interactions",
        "Praise": "Social Interactions",
        "Appearance": "People & Descriptions",
        "Clothes": "People & Descriptions",
        "Colors": "People & Descriptions",
        "Personality": "People & Descriptions",
        "Money": "Daily Life",
        "Daily Schedule": "Daily Life",
        "Habits": "Daily Life",
        "Housework": "Daily Life",
        "Mistakes": "Daily Life",
        "Bad Luck": "Daily Life",
        "Family 1": "Family",
        "Family 2": "Family",
        "Career": "Work & Career",
        "Interviews": "Work & Career",
        "Office Work": "Work & Career",
        "Work": "Work & Career",
        "Shopping": "Shopping",
        "Online Shopping": "Shopping",
        "Bargaining": "Shopping",
        "Transport": "Travel",
        "Traveling 1": "Travel",
        "Traveling 2": "Travel",
        "Catching a Flight": "Travel",
        "Going Abroad": "Travel",
        "Renting": "Travel",
        "Hometown": "Locations",
        "Locations": "Locations",
        "Directions": "Locations",
        "Personal Information": "Personal & Communication",
        "Phone-Calls": "Personal & Communication",
        "Communications": "Personal & Communication",
        "Time": "Time & Dates",
        "Dates": "Time & Dates",
        "Rooms": "Home & Living",
        "Weather": "Home & Living",
        "Leisure": "Hobbies & Free Time",
        "Sports": "Hobbies & Free Time",
        "Spare Time": "Hobbies & Free Time",
        "Sports Competitions": "Hobbies & Free Time",
        "Movies": "Hobbies & Free Time",
        "Hiking": "Hobbies & Free Time",
        "Comparing": "Cognitive & Emotions",
        "Shocked": "Cognitive & Emotions",
        "Weight Loss": "Health",
        "Health": "Health",
        "Pets": "Nature & Animals",
        "Nature": "Nature & Animals",
        "Environment": "Nature & Animals",
        "China 1": "Culture",
        "China 2": "Culture"
    }

    df["Category"] = df["Dimension"].map(dimension_to_category).fillna("Other")
    return df

def extract_tag_segment(meaning, tag):
    if pd.isna(meaning):
        return "", meaning
    parts = re.split(r'(\b[A-Z]{1,4}\.)', meaning)
    highlighted = ""
    building = False
    for i, part in enumerate(parts):
        if part == tag:
            building = True
            highlighted += f"**{part}"
        elif building and re.match(r"\b[A-Z]{1,4}\.", part):
            break
        elif building:
            highlighted += f" {part}"
    return highlighted.strip(), meaning

# Define grammatical groups
grammar_groups = {
    "Verbs": ["V.", "V.O.", "S.V.", "R.V.", "AUX.", "COV.", "B.F."],
    "Nouns & Pronouns": ["N.", "NOUN", "PR.", "SUF."],
    "Adjectives": ["A.M.", "ATTR."],
    "Adverbs": ["ADV."],
    "Measure/Classifiers": ["M.", "M.P."],
    "Particles": ["P.W."],
    "Conjunctions": ["CONS.", "CONJ."],
    "Numbers": ["NUM."]
}

# Load data
df = load_data()

# Sidebar filters

# Search section first
st.sidebar.markdown("## 🔍 Search")
if "last_search" not in st.session_state:
    st.session_state.last_search = ""

search_text = st.sidebar.text_input("Search word or pinyin", value="")

if search_text:
    st.session_state.last_search = search_text
whole_word_only = st.sidebar.checkbox("Match whole word only")
if st.sidebar.button("Reset All"):
    st.rerun()
st.sidebar.markdown("---")
group_options = ["All"] + list(grammar_groups.keys())
selected_group = st.sidebar.selectbox("Select grammatical category:", group_options, key="sidebar_group")

# Map tags to full descriptions
tag_descriptions = {
    "V.": "Verb",
    "V.O.": "Verb-Object",
    "S.V.": "Subject-Verb",
    "R.V.": "Reduplicated Verb",
    "AUX.": "Auxiliary Verb",
    "COV.": "Coverb",
    "B.F.": "Base Form",
    "N.": "Noun",
    "NOUN": "Noun",
    "PR.": "Pronoun",
    "SUF.": "Suffix",
    "A.M.": "Adjective Modifier",
    "ATTR.": "Attributive",
    "ADV.": "Adverb",
    "M.": "Measure Word",
    "M.P.": "Measure Word / Particle",
    "P.W.": "Particle Word",
    "CONS.": "Conjunction",
    "CONJ.": "Conjunction",
    "NUM.": "Number"
}

# Create reverse lookup for selectbox
tag_display = {v: k for k, v in tag_descriptions.items() if k in {tag for tags in df["Tags"] for tag in tags}}
tag_display_options = ["All"] + sorted(tag_display.keys())
selected_tag_label = st.sidebar.selectbox("Or select specific grammatical tag:", tag_display_options, key="sidebar_tag")
selected_tag = tag_display[selected_tag_label] if selected_tag_label != "All" else "All"

# Category and Subcategory filter
all_categories = sorted(df["Category"].unique())
selected_category = st.sidebar.selectbox("Topic Category:", ["All"] + all_categories, key="sidebar_cat")

subcat_options = df[df["Category"] == selected_category]["Dimension"].unique() if selected_category != "All" else df["Dimension"].unique()
selected_subcat = st.sidebar.selectbox("Subtopic (Dimension):", ["All"] + sorted(subcat_options), key="sidebar_subcat")





# Filter logic
filtered = df.copy()

if selected_group != "All":
    group_tags = grammar_groups[selected_group]
    filtered = filtered[filtered["Tags"].apply(lambda tags: any(tag in tags for tag in group_tags))]
elif selected_tag != "All":
    filtered = filtered[filtered["Tags"].apply(lambda tags: selected_tag in tags)]

if selected_category != "All":
    filtered = filtered[filtered["Category"] == selected_category]
if selected_subcat != "All":
    filtered = filtered[filtered["Dimension"] == selected_subcat]
import difflib
if search_text:
    search_lower = search_text.lower()
    def fuzzy_match(text):
        if whole_word_only:
            return re.search(rf'\b{re.escape(search_lower)}\b', text, re.IGNORECASE) is not None
        return search_lower in text.lower() or difflib.SequenceMatcher(None, search_lower, text.lower()).ratio() > 0.7
    filtered = filtered[filtered["Characters / Traditional"].apply(fuzzy_match) |
                        filtered["Pinyin"].apply(fuzzy_match) |
                        filtered["Meaning"].apply(fuzzy_match)]

if st.session_state.last_search and not (selected_group != "All" or selected_tag != "All" or selected_category != "All" or selected_subcat != "All"):
    st.markdown(f"🔍 Word searched: \"{st.session_state.last_search}\"")

# # Display results
# st.markdown(f"### Showing {len(filtered)} words")

# for _, row in filtered.iterrows():
#     char = row["Characters / Traditional"]
#     pinyin = row["Pinyin"]
#     meaning = row["Meaning"]
#     tags = row["Tags"]
#     tag_highlight = ""

#     # Choose which tag to highlight
#     tag_to_highlight = selected_tag if selected_tag != "All" else None
#     if selected_group != "All":
#         for gtag in grammar_groups[selected_group]:
#             if gtag in tags:
#                 tag_to_highlight = gtag
#                 break

#     if tag_to_highlight:
#         tag_highlight, _ = extract_tag_segment(meaning, tag_to_highlight)
#         if tag_highlight:
#             highlighted_html = meaning.replace(tag_highlight, f'<mark style="background-color:#d4edda; padding:2px; border-radius:3px;">{tag_highlight}</mark>', 1)
#         else:
#             highlighted_html = meaning

#     with st.container():
#         card_color = "#edf7f1"  # soft eco-inspired green background
#         border_color = "#cde3d4"
#         st.markdown(f"""
#         <div style='border: 2px solid {border_color}; border-radius: 16px; padding: 1.2rem; margin-bottom: 1.5rem; background-color: {card_color}; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);'>
#             <h2 style='margin-bottom: 0.2rem; font-size: 1.8rem;'>{char}</h2>
#             <p style='margin: 0.2rem 0;'><strong></strong> <code style='font-size: 1.1rem;'>{pinyin}</code></p>
#             <p style='margin-top: 0.8rem;'><strong></strong> {meaning}</p>
#         """, unsafe_allow_html=True)

#         # if tag_highlight:
#         #     st.markdown(f"<p style='margin-top: 0.8rem;'><strong>Meaning:</strong><br>{highlighted_html}</p>", unsafe_allow_html=True)
#         # else:
#         #     if search_text:
#         #         pattern = re.compile(re.escape(search_text), re.IGNORECASE)
#         #         highlighted_meaning = pattern.sub(lambda m: f'<mark style="background-color:#fff3cd;">{m.group(0)}</mark>', meaning)
#         #         st.markdown(f"<p style='margin-top: 0.8rem;'><strong>Meaning:</strong><br>{highlighted_meaning}</p>", unsafe_allow_html=True)
#         #     else:
#         #         st.markdown(f"<p style='margin-top: 0.8rem;'><strong>Meaning:</strong> {meaning}</p>", unsafe_allow_html=True)

#         # st.markdown(f"<p style='color: #4d704d; font-size: 0.9rem;'><strong>Tags:</strong> {', '.join(tags)}</p>", unsafe_allow_html=True)
#         # st.button(f"🔊 (audio coming soon)", key=f"listen_{uuid.uuid4()}")
#         st.markdown("</div>", unsafe_allow_html=True)


tab1, tab2 = st.tabs(["🔖 Flashcards View", "📊 Table View"])

with tab1:
    st.markdown(f"### Showing {len(filtered)} words")
    for cat in sorted(filtered["Category"].unique()):
        cat_df = filtered[filtered["Category"] == cat]
        with st.expander(cat, expanded=True):
            for dim in sorted(cat_df["Dimension"].unique()):
                st.markdown(f"#### 📘 {dim}")
                for _, row in cat_df[cat_df["Dimension"] == dim].iterrows():
                    char = row["Characters / Traditional"]
                    pinyin = row["Pinyin"]
                    meaning = row["Meaning"]
                    tags = row["Tags"]
                    tag_highlight = ""
                    highlighted_html = meaning

                    # Highlight specific tag if selected
                    tag_to_highlight = selected_tag if selected_tag != "All" else None
                    if selected_group != "All":
                        for gtag in grammar_groups[selected_group]:
                            if gtag in tags:
                                tag_to_highlight = gtag
                                break

                    if tag_to_highlight:
                        tag_highlight, _ = extract_tag_segment(meaning, tag_to_highlight)
                        if tag_highlight:
                            highlighted_html = meaning.replace(tag_highlight, f'<mark style="background-color:#d4edda; padding:2px; border-radius:3px;">{tag_highlight}</mark>', 1)

                    st.markdown(f"""
                        <div style='border: 2px solid #cde3d4; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; background-color: #edf7f1;'>
                            <div style='display: flex; justify-content: space-between;'>
                                <div style='flex: 1;'>
                                    <h3 style='margin: 0;'>{char}</h3>
                                    <p><code>{pinyin}</code></p>
                                </div>
                                <div style='flex: 2;'>
                                    <p>{highlighted_html}</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

with tab2:
    st.dataframe(filtered, use_container_width=True)
