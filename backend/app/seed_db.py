# Script to seed the database with initial test data

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    logger.info("Seeding database with initial data...")
    db = SessionLocal()
    
    try:
        # Check if we already have data
        existing_chats = db.query(models.Chat).count()
        if existing_chats > 0:
            logger.info(f"Database already contains {existing_chats} chats. Skipping seeding.")
            return
        
        # Create a sample chat
        chat1 = models.Chat(
            title="Introduction to Calculus",
            create_time=datetime.utcnow()
        )
        db.add(chat1)
        db.flush()  # Flush to get the chat ID
        
        # Add messages to the chat
        messages = [
            models.Message(
                chat_id=chat1.id,
                role="user",
                content="Can you explain what a derivative is in calculus?",
                timestamp=datetime.utcnow()
            ),
            models.Message(
                chat_id=chat1.id,
                role="model",
                content="In calculus, a derivative measures the rate at which a function changes at a specific point. It's the slope of the tangent line to the function at that point. The derivative of a function f(x) is denoted as f'(x) or df/dx.\n\nFor example, if f(x) = x², then f'(x) = 2x. This means that at any point x, the rate of change of x² is 2x.\n\nDerivatives are fundamental in calculus and have many applications in physics, engineering, economics, and other fields where we need to understand how quantities change with respect to other quantities.",
                timestamp=datetime.utcnow()
            )
        ]
        db.add_all(messages)
        
        # Create another sample chat
        chat2 = models.Chat(
            title="Algebra Help",
            create_time=datetime.utcnow()
        )
        db.add(chat2)
        db.flush()  # Flush to get the chat ID
        
        # Add messages to the second chat
        messages = [
            models.Message(
                chat_id=chat2.id,
                role="user",
                content="How do I solve a quadratic equation?",
                timestamp=datetime.utcnow()
            ),
            models.Message(
                chat_id=chat2.id,
                role="model",
                content="A quadratic equation has the form ax² + bx + c = 0, where a ≠ 0.\n\nThere are several ways to solve it:\n\n1. **Factoring**: If you can rewrite ax² + bx + c as (px + q)(rx + s) = 0, then the solutions are x = -q/p and x = -s/r.\n\n2. **Quadratic Formula**: x = (-b ± √(b² - 4ac)) / (2a)\n   This formula gives you both solutions at once.\n\n3. **Completing the Square**: Rearrange the equation to isolate x² and x terms, then add and subtract terms to create a perfect square trinomial.\n\nThe quadratic formula is the most general method and works for any quadratic equation.",
                timestamp=datetime.utcnow()
            )
        ]
        db.add_all(messages)
        
        db.commit()
        logger.info("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()