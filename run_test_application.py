import asyncio
from datetime import datetime
from msme_underwriting.orchestrator import MSMELoanOrchestrator
from msme_underwriting.models.loan_application import (
    LoanApplication,
    LoanContext,
    UploadedFile,
    ProcessingOptions,
)

async def main():
    """
    This function initializes the orchestrator and processes a sample loan application.
    """
    print("Initializing the MSME Loan Orchestrator...")
    # Initialize orchestrator
    orchestrator = MSMELoanOrchestrator()

    # Create a sample loan application to process
    # This data mimics the input the system would receive
    print("Creating a sample loan application...")
    loan_application = LoanApplication(
        thread_id=f"loan_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        user_id="test_user_001",
        loan_context=LoanContext(
            loan_type="MSM_supply_chain",
            loan_amount=5000000,
            application_timestamp=datetime.utcnow()
        ),
        uploaded_files=[
            UploadedFile(
                file_name="sample_documents.zip",
                # This is a placeholder path; the file doesn't need to exist for this test
                file_path="/uploads/test_user_001/sample_documents.zip",
                file_size=15728640,
                upload_timestamp=datetime.utcnow(),
                file_type="application/zip"
            )
        ],
        processing_options=ProcessingOptions(
            max_pages_per_document=50,
            include_raw_responses=False,
            vision_model="gpt-4o",
            confidence_threshold=0.7,
            enable_ocr=True,
            language="en"
        )
    )

    # Process the application through the workflow
    print(f"Starting the underwriting process for thread_id: {loan_application.thread_id}")
    print("-" * 50)
    
    final_state = await orchestrator.process_loan_application(loan_application)

    print("-" * 50)
    print("Workflow processing finished.")

    # Print the final report or any errors
    if final_state.has_errors:
        print("\n🚨 The process encountered errors:")
        for error in final_state.errors:
            print(f"  - Agent '{error.get('agent')}': {error.get('error')}")
    elif final_state.final_report:
        print("\n✅ Final Report Generated Successfully!")
        print(f"  Recommendation: {final_state.final_report.loan_recommendation.primary_recommendation}")
        print(f"  Risk Grade: {final_state.final_report.risk_assessment_summary.risk_grade}")
        print(f"  Recommended Amount: {final_state.final_report.loan_recommendation.recommended_loan_amount}")
    else:
        print("\n🤔 The workflow completed without a final report or explicit errors.")
        print(f"Final workflow status: {final_state.workflow_status}")


if __name__ == "__main__":
    # This runs the main async function
    asyncio.run(main())