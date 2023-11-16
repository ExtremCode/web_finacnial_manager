from yoyo import step


steps = [
    step("""create schema financial;""",
          """drop schema financial cascade;""")
]
