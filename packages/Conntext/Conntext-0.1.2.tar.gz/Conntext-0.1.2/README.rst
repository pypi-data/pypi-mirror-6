Conntext
========
Context managers for secure and atomic database connectivity

Rationale
---------
- Each context being a single atomic process ("either all occur, or nothing occurs")
- No manual ``commit`` (success), ``rollback`` (fail) or ``close`` (either)
- No ORM

Usage
-----
Without Conntext,

.. code-block:: python

    conn = sqlite3.connect(":memory:")
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("CREATE TABLE person (name)")
            cursor.execute("INSERT INTO person (name) VALUES (?)",
                            ["microamp"])
        except Exception:
            raise
        finally:
            cursor.close()
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()

With Conntext,

.. code-block:: python

    from conntext import conntext

    with conntext.conn(sqlite3.connect(":memory:")) as conn:
       with conntext.cursor(conn.cursor()) as cursor:
            cursor.execute("CREATE TABLE person (name)")
            cursor.execute("INSERT INTO person (name) VALUES (?)",
                           ["microamp"])

License
-------
All the code is licensed under the GNU Lesser General Public License (v3+).
