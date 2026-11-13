import chromadb

chroma=chromadb.Client()

company_knowledge_base=chroma.create_collection(name="company_knowledge_base")

company_knowledge_base.add(
    ids=["c0", "c1", "c2", "c3"],
    documents=[
        (
            "Leave Policy - Maternity Leave\n"
            "Maternity leave is 26 weeks of paid leave "
            "for the first two children."
        ),
        (
            "Medical Policy - Maternity Cover\n"
            "Hospitalization for childbirth is covered "
            "up to 75,000 rupees."
        ),
        (
            "Travel Expense - Reimbursement\n"
            "Submit expense claims within 30 days of the trip. "
            "Approved claims are reimbursed within 7 working days."
        ),
        (
            "Tech Docs - Deployment Windows\n"
            "Production deployments are allowed on Tuesdays "
            "and Thursdays between 11 AM and 4 PM."
        ),
    ],
)



results = company_knowledge_base.query(
    query_texts=["What are the benefits of Maternity Leave?"],
    n_results=1,
)

print(results["documents"][0])



