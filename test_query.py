"""Quick test for the enhanced query_documents function."""

from tools import query_documents

# Sample document content
sample_doc = """
Product Information Document

Our company offers the following services:

1. Web Development: We create modern, responsive websites using the latest technologies.
   Price: Starting from $2000
   Timeline: 4-6 weeks

2. Mobile App Development: Native and cross-platform mobile applications.
   Price: Starting from $5000
   Timeline: 8-12 weeks

3. Cloud Solutions: AWS, Azure, and Google Cloud infrastructure setup and management.
   Price: Custom pricing based on requirements
   Timeline: 2-4 weeks

4. AI/ML Solutions: Machine learning models and AI integration.
   Price: Starting from $10000
   Timeline: 12-16 weeks

Business Hours: Monday to Friday, 9 AM - 6 PM
Contact: support@company.com
Phone: +1-555-0123
"""

# Test queries
test_queries = [
    "What services do you offer?",
    "How much does mobile app development cost?",
    "What are your business hours?",
    "Tell me about AI solutions",
    "How long does web development take?"
]

print("=" * 70)
print("Testing Enhanced query_documents Function")
print("=" * 70)

for i, query in enumerate(test_queries, 1):
    print(f"\n{i}. Query: {query}")
    print("-" * 70)
    result = query_documents(query, sample_doc)
    print(f"Result:\n{result}")
    print("=" * 70)

print("\nTest completed!")
