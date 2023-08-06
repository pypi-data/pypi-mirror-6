rename_entity_type('Category', 'FAQSection')
rename_entity_type('Question', 'FAQuestion')
rename_relation_type('in_category', 'in_faq_section')

rename_attribute('FAQuestion', 'title', 'question')

add_attribute('FAQuestion', 'answer')
add_attribute('FAQuestion', 'answer_format')
rql('SET FAQ answer C, FAQ answer_format F WHERE A answers FAQ, A content C, '
    'A content_format F')

drop_entity_type('Answer')
drop_relation_type('answers')
