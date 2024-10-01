import unittest
from backend.utils.categorization import get_category_case
from models.card import Card
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestCategorization(unittest.TestCase):
    def setUp(self):
        # Setup in-memory SQLite for testing
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Create tables as needed
        Card.metadata.create_all(self.engine)
    
    def test_main_set_categorization(self):
        card = Card(frame_effects=None, promo_types=None)
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Main Set')
    
    def test_showcase_categorization(self):
        card = Card(frame_effects=['showcase'], promo_types=None)
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Showcases')
    
    def test_extended_art_categorization(self):
        card = Card(frame_effects=['extendedart'], promo_types=None)
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Extended Art')
    
    def test_fracture_foils_categorization(self):
        card = Card(frame_effects=None, promo_types=['fracturefoil'])
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Fracture Foils')
    
    def test_borderless_cards_categorization(self):
        card = Card(frame_effects=['borderless'], promo_types=None)
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Borderless Cards')
    
    def test_promos_categorization(self):
        card = Card(frame_effects=None, promo_types=['promo'])
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Promos')
    
    def test_art_variants_categorization(self):
        card = Card(frame_effects=['other'], promo_types=['other'])
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Art Variants')
    
    def test_multiple_frame_effects(self):
        card = Card(frame_effects=['showcase', 'extendedart'], promo_types=None)
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Showcases')  # Assuming 'showcase' takes precedence
    
    def test_multiple_promo_types(self):
        card = Card(frame_effects=None, promo_types=['promo', 'fracturefoil'])
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Fracture Foils')  # Assuming 'fracturefoil' takes precedence
    
    def test_empty_arrays(self):
        card = Card(frame_effects=[], promo_types=[])
        self.session.add(card)
        self.session.commit()
        category_case = get_category_case(Card)
        result = self.session.query(category_case).filter(Card.id == card.id).one()
        self.assertEqual(result.category, 'Main Set')
    
    def tearDown(self):
        self.session.close()
        self.engine.dispose()

if __name__ == '__main__':
    unittest.main()
