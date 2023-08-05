"""
All processing that follows loading of s3 km data into tables.
"""

def sql_resolve():
    """SQL to associate an emailid with each event, if available."""

    return """
    -- 1. if event already had an email, set it
    UPDATE events e
       SET emailid = u.userid
      FROM users u
     WHERE e.emailid ISNULL
       AND e.userid = u.userid
       AND isemail(u.name);

    -- 2. resolve emails via aliases
    -- XXX what if a e.userid has multiple aliases?
    UPDATE events e
       SET emailid = u.userid
      FROM aliases a, users u
     WHERE e.emailid ISNULL
       AND e.userid = a.userid
       AND a.aliasid = u.userid
       AND isemail(u.name);
    """
