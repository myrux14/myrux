import streamlit.components.v1 as components


def inject_google_analytics():

    components.html(
        """
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>

        <script>

          window.dataLayer = window.dataLayer || [];

          function gtag(){
            dataLayer.push(arguments);
          }

          gtag('js', new Date());

          gtag('config', 'G-D3JGDX7T7K');

        </script>
        """,
        height=0,
        width=0,
    )