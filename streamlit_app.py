# # # import streamlit as st

# # # st.title("🎈 My new app")
# # # st.write(
# # #     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# # # )

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
#         height=1000,
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

# Database connection function
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        st.secrets["postgres"]["url"],
        cursor_factory=RealDictCursor
    )

# Data fetching function
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

# Update function
def update_message(id, role, content):
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE messages 
            SET role = %s, content = %s
            WHERE id = %s
        """, (role, content, id))
    conn.commit()

try:
    # Fetch data
    df = get_messages()
    
    # Display total count
    st.write(f"Total messages: {len(df)}")
    
    # Display the editable dataframe
    edited_df = st.data_editor(
        df,
        column_config={
            "id": st.column_config.NumberColumn(
                "ID",
                required=True,
                editable=False,
            ),
            "role": st.column_config.TextColumn(
                "Role",
                required=True,
                max_chars=50,
            ),
            "content": st.column_config.TextColumn(
                "Content",
                width="large",
                required=True,
            ),
            "timestamp": st.column_config.TextColumn(
                "Timestamp",
                editable=False,
            )
        },
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True
    )

    # Check for changes
    if st.button("Save Changes"):
        changes_made = False
        for index, row in edited_df.iterrows():
            original_row = df.iloc[index]
            if (row['role'] != original_row['role'] or 
                row['content'] != original_row['content']):
                update_message(row['id'], row['role'], row['content'])
                changes_made = True
        
        if changes_made:
            st.success("Changes saved successfully!")
            st.cache_data.clear()  # Clear cache to refresh data
            st.rerun()  # Rerun the app to show updated data
        else:
            st.info("No changes detected")

except Exception as e:
    st.error(f"Error: {str(e)}")