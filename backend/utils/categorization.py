from sqlalchemy import case, and_, or_

def get_category_case(Card):
    main_set_condition = and_(
        or_(Card.frame_effects == None, Card.frame_effects == '[]'),
        or_(Card.promo_types == None, Card.promo_types == '[]')
    )

    category_case = case(
        (Card.frame_effects.contains('"showcase"'), 'Showcases'),
        (Card.frame_effects.contains('"extendedart"'), 'Extended Art'),
        (Card.promo_types.contains('"fracturefoil"'), 'Fracture Foils'),
        (Card.frame_effects.contains('"borderless"'), 'Borderless Cards'),
        (Card.promo_types.contains('"promo"'), 'Promos'),
        (main_set_condition, 'Main Set'),
        else_='Art Variants'
    ).label('category')

    return category_case
from sqlalchemy import case, and_, or_

def get_card_category_case(Card):
    """
    Returns a SQLAlchemy case statement to categorize cards based on their attributes.
    """
    main_set_condition = and_(
        or_(Card.frame_effects == None, Card.frame_effects == []),
        or_(Card.promo_types == None, Card.promo_types == [])
    )

    category_case = case(
        (Card.frame_effects.contains(['showcase']), 'Showcases'),
        (Card.frame_effects.contains(['extendedart']), 'Extended Art'),
        (Card.promo_types.contains(['fracturefoil']), 'Fracture Foils'),
        (Card.frame_effects.contains(['borderless']), 'Borderless Cards'),
        (Card.promo_types.contains(['promo']), 'Promos'),
        (main_set_condition, 'Main Set'),
        else_='Art Variants'
    ).label('category')

    return category_case
