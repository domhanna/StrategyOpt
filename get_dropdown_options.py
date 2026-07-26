def get_dropdown_options(soup, select_name):

    """
    Extract dropdown object lists from parsed HTML content (soup).

    Args:
        bs4.BeautifulSoup: parsed HTML content.
        select_name (str): The 'name' attribute of the <select> element to extract
            options from

    Returns:
        list[tuple[str, str]]: (display_text, value) pairs for each
            <option> found. Empty list if no matching <select> exists.

    """

    select_obj = soup.find("select", attrs={"name": select_name})
    if select_obj is None:
        return []
    
    tag_objects = select_obj.find_all("option")
    return [(option.text.strip(), option["value"]) for option in tag_objects]
        
 