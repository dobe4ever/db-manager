# # import streamlit as st

# # st.title("🎈 My new app")
# # st.write(
# #     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# # )

# import streamlit as st
# import pandas as pd
# import psycopg2
# from psycopg2.extras import RealDictCursor

# # Page config
# st.set_page_config(page_title="Messages Viewer", layout="wide")
# st.title("Messages Viewer")

# # Database connection function
# @st.cache_resource
# def init_connection():
#     return psycopg2.connect(
#         st.secrets["postgres"]["url"],
#         cursor_factory=RealDictCursor
#     )

# # Data fetching function
# @st.cache_data(ttl=60)
# def get_messages():
#     conn = init_connection()
#     with conn.cursor() as cur:
#         cur.execute("""
#             SELECT id, role, content, 
#                    to_char(timestamp, 'YYYY-MM-DD HH24:MI:SS') as timestamp 
#             FROM messages 
#             ORDER BY timestamp DESC
#         """)
#         return pd.DataFrame(cur.fetchall())

# try:
#     # Fetch data
#     df = get_messages()
    
#     # Display total count
#     st.write(f"Total messages: {len(df)}")
    
#     # Display the interactive dataframe
#     st.dataframe(
#         df,
#         column_config={
#             "id": "ID",
#             "role": "Role",
#             "content": st.column_config.TextColumn(
#                 "Content",
#                 width="large",
#                 help="Message content"
#             ),
#             "timestamp": "Timestamp"
#         },
#         hide_index=True,
#         use_container_width=True
#     )

# except Exception as e:
#     st.error(f"Error connecting to database: {str(e)}")

import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Page config
st.set_page_config(page_title="Messages Viewer", layout="wide")
st.title("Messages Viewer")

@st.cache_resource
def init_connection():
    return psycopg2.connect(
        st.secrets["postgres"]["url"],
        cursor_factory=RealDictCursor
    )

@st.cache_data(ttl=60)
def get_messages():
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, role, content, 
                   to_char(timestamp, 'YYYY-MM-DD HH24:MI:SS') as timestamp 
            FROM messages 
            ORDER BY timestamp DESC
        """)
        return pd.DataFrame(cur.fetchall())

try:
    # Fetch data
    df = get_messages()
    
    # Display total count
    st.write(f"Total messages: {len(df)}")
    
    # Create a preview of content (first 50 characters)
    df['content_preview'] = df['content'].str[:50] + '...'
    
    # Display the interactive dataframe
    selected_indices = st.dataframe(
        df[['id', 'role', 'content_preview', 'timestamp']],
        column_config={
            "id": "ID",
            "role": "Role",
            "content_preview": st.column_config.TextColumn(
                "Content Preview",
                width="large",
                help="Click a row to see full message"
            ),
            "timestamp": "Timestamp"
        },
        hide_index=True,
        use_container_width=True,
        height=500,
        selection_mode = "single"
        # selection="single"  # Enable single row selection
    )

    # Show selected message in detail
    if selected_indices:
        selected_row = df.iloc[selected_indices]
        with st.expander("Selected Message", expanded=True):
            cols = st.columns([1, 2, 1])
            with cols[0]:
                st.write("**ID:**", selected_row['id'].iloc[0])
                st.write("**Role:**", selected_row['role'].iloc[0])
                st.write("**Timestamp:**", selected_row['timestamp'].iloc[0])
            with cols[1]:
                st.text_area(
                    "Full Content",
                    value=selected_row['content'].iloc[0],
                    height=200,
                    disabled=True
                )

except Exception as e:
    st.error(f"Error connecting to database: {str(e)}")