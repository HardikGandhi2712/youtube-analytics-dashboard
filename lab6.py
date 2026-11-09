
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="YouTube Analytics", layout="wide")

st.title("YouTube Channel Analytics Dashboard")
st.write("Explore and analyse YouTube channel statistics using graphs.")

file = st.file_uploader("Upload YouTube Dataset", type=["csv"])

if file is not None:
    try:
        df = pd.read_csv(file, encoding="latin1", engine="python")
        st.success("Dataset uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        st.stop()

    df.columns = df.columns.str.strip()

    required_columns = ["Youtuber", "subscribers", "video views", "uploads", "category"]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        st.stop()

    numeric_columns = [
        "subscribers", "video views", "uploads", "created_year",
        "video_views_for_the_last_30_days", "highest_monthly_earnings"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Youtuber"])

    st.sidebar.title("Dashboard Filters")

    if "category" in df.columns:
        categories = sorted(df["category"].dropna().unique().tolist())
        selected_category = st.sidebar.multiselect(
            "Select Category", categories, default=categories
        )
        df = df[df["category"].isin(selected_category)]

    if "Country" in df.columns:
        countries = sorted(df["Country"].dropna().unique().tolist())
        selected_country = st.sidebar.multiselect(
            "Select Country", countries, default=countries
        )
        df = df[df["Country"].isin(selected_country)]

    if "channel_type" in df.columns:
        channel_types = sorted(df["channel_type"].dropna().unique().tolist())
        selected_type = st.sidebar.multiselect(
            "Select Channel Type", channel_types, default=channel_types
        )
        df = df[df["channel_type"].isin(selected_type)]

    if "created_year" in df.columns:
        years = df["created_year"].dropna()
        if not years.empty:
            min_year = int(years.min())
            max_year = int(years.max())

            if min_year < max_year:
                selected_years = st.sidebar.slider(
                    "Select Creation Year",
                    min_year,
                    max_year,
                    (min_year, max_year)
                )
                df = df[
                    df["created_year"].between(
                        selected_years[0], selected_years[1]
                    )
                ]

    if df.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    st.header("YouTube Dashboard")

    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Channels", len(df))
        col2.metric("Total Subscribers", f"{df['subscribers'].sum():,.0f}")
        col3.metric("Average Subscribers", f"{df['subscribers'].mean():,.0f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Total Video Views", f"{df['video views'].sum():,.0f}")
        col5.metric("Average Video Views", f"{df['video views'].mean():,.0f}")
        col6.metric("Average Uploads", f"{df['uploads'].mean():.0f}")

    st.divider()

    tabs = st.tabs([
        "Overview",
        "Data Analysis",
        "Visualizations",
        "Insights",
        "Dataset"
    ])

    with tabs[0]:
        st.header("Channel Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 YouTube Channels")

            top_channels = df.nlargest(10, "subscribers")

            fig, ax = plt.subplots()
            ax.barh(
                top_channels["Youtuber"],
                top_channels["subscribers"],
                label="Subscribers"
            )
            ax.set_xlabel("Subscribers")
            ax.set_ylabel("YouTube Channels")
            ax.set_title("Top 10 Channels by Subscribers")
            ax.invert_yaxis()
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            st.write(
                "This graph compares the subscriber counts of the top 10 channels."
            )

        with col2:
            st.subheader("Channels by Category")

            category_count = df.groupby("category").size().sort_values(
                ascending=False
            ).head(10)

            fig, ax = plt.subplots()
            ax.bar(
                category_count.index,
                category_count.values,
                label="Number of Channels"
            )
            ax.set_title("Number of Channels by Category")
            ax.set_xlabel("Category")
            ax.set_ylabel("Number of Channels")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            st.write(
                "This graph shows how channels are distributed across different categories."
            )

    with tabs[1]:
        st.header("Data Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Subscribers by Category")

            category_subscribers = (
                df.groupby("category")["subscribers"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            fig, ax = plt.subplots()
            ax.bar(
                category_subscribers.index,
                category_subscribers.values,
                label="Subscribers"
            )
            ax.set_title("Total Subscribers by Category")
            ax.set_xlabel("Category")
            ax.set_ylabel("Total Subscribers")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            st.write(
                "This graph helps identify which categories have the highest total subscribers."
            )

        with col2:
            st.subheader("Top 10 Channels by Video Views")

            top_views = df.nlargest(10, "video views")

            fig, ax = plt.subplots()
            ax.bar(
                top_views["Youtuber"],
                top_views["video views"],
                label="Video Views"
            )
            ax.set_title("Top 10 Channels by Video Views")
            ax.set_xlabel("YouTube Channel")
            ax.set_ylabel("Video Views")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            st.write(
                "This graph compares the total video views of the top 10 channels."
            )

        st.subheader("Select a Channel")

        channel_list = sorted(df["Youtuber"].unique().tolist())

        selected_channel = st.selectbox(
            "Choose a YouTube Channel",
            ["All Channels"] + channel_list
        )

        if selected_channel != "All Channels":
            channel_data = df[df["Youtuber"] == selected_channel].iloc[0]

            col1, col2, col3 = st.columns(3)
            col1.metric("Subscribers", f"{channel_data['subscribers']:,.0f}")
            col2.metric("Video Views", f"{channel_data['video views']:,.0f}")
            col3.metric("Uploads", f"{channel_data['uploads']:,.0f}")

    with tabs[2]:
        st.header("YouTube Growth Analysis")

        st.subheader("Average Subscribers by Creation Year")

        if "created_year" in df.columns:
            yearly_data = (
                df.groupby("created_year")["subscribers"]
                .mean()
                .dropna()
                .sort_index()
            )

            fig, ax = plt.subplots()
            ax.plot(
                yearly_data.index,
                yearly_data.values,
                marker="o",
                label="Average Subscribers"
            )
            ax.set_title("Average Subscribers by Channel Creation Year")
            ax.set_xlabel("Creation Year")
            ax.set_ylabel("Average Subscribers")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            st.write(
                "This line graph compares the average subscribers of channels created in different years."
            )

        st.subheader("Subscribers vs Video Views")

        scatter_data = df.dropna(subset=["subscribers", "video views"])

        fig, ax = plt.subplots()
        ax.scatter(
            scatter_data["subscribers"],
            scatter_data["video views"],
            label="YouTube Channels"
        )
        ax.set_title("Subscribers vs Video Views")
        ax.set_xlabel("Subscribers")
        ax.set_ylabel("Video Views")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

        st.write(
            "This scatter plot shows the relationship between subscribers and video views."
        )

    with tabs[3]:
        st.header("Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            top_channel = df.loc[df["subscribers"].idxmax(), "Youtuber"]
            st.success(f"Most subscribed channel: {top_channel}")

            top_category = (
                df.groupby("category")["subscribers"]
                .sum()
                .idxmax()
            )
            st.info(f"Category with highest subscribers: {top_category}")

        with col2:
            average_subscribers = df["subscribers"].mean()
            st.metric(
                "Average Subscribers per Channel",
                f"{average_subscribers:,.0f}"
            )

            average_views = df["video views"].mean()
            st.metric(
                "Average Views per Channel",
                f"{average_views:,.0f}"
            )

        with st.expander("Read More About the Analysis"):
            st.write(
                "The dashboard analyses YouTube channels based on subscribers, "
                "video views, uploads, categories and creation years. "
                "The filters help users explore different parts of the dataset. "
                "The graphs make it easier to compare channel performance "
                "and understand the distribution of channels."
            )

    with tabs[4]:
        st.header("YouTube Dataset")

        st.write("Total records:", len(df))
        st.dataframe(df, use_container_width=True)

        with st.expander("Dataset Information"):
            st.write("Number of rows:", df.shape[0])
            st.write("Number of columns:", df.shape[1])
            st.write("Missing values in each column:")
            st.write(df.isnull().sum())

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Filtered Dataset",
            data=csv,
            file_name="youtube_filtered_data.csv",
            mime="text/csv"
        )

    st.divider()

    st.caption("YouTube Channel Analytics Dashboard | Streamlit")

else:
    st.info("Please upload your YouTube CSV dataset to view the dashboard.")
