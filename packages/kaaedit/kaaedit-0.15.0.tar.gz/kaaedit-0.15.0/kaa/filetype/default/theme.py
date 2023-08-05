from kaa.theme import Theme, Style, Overlay

DefaultThemes = {
    'basic':
        Theme([
            Style('default', 'default', 'default'),
            Style('lineno', 'White', 'Blue'),
            Style('parenthesis_cur', 'White', 'Blue'),
            Style('parenthesis_match', 'Red', 'Yellow'),

            Style('keyword', 'Magenta', 'default'),
            Style('constant', 'Red', 'default'),
            Style('directive', 'Orange', 'default'),
            Style('comment', 'Cyan', 'default'),
            Style('string', 'Blue', 'default'),
            Style('number', 'Green', 'default'),

            Overlay('cursor_row', None, 'Base02'),   
            Overlay('breakpoint', None, 'Base02'),   
            Overlay('current_row', None, 'Yellow'),   
        ]),
    
}
