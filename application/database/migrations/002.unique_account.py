from yoyo import step


__depends__ = {'000.schema', '001.create_tables'}

steps = [
    step("""
        ALTER TABLE IF EXISTS account
        ADD CONSTRAINT unique_acc UNIQUE (person_id, acc_name)""",
        """
        ALTER TABLE IF EXISTS account
        DROP CONSTRAINT IF EXISTS unique_acc""")
]
