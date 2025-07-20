from supabase import create_client

supabase = create_client(st.secrets["supabase_url"], st.secrets["supabase_api_key"])

# Example: Get all users
data = supabase.table("users").select("*").execute()
st.write(data.data)
