# Developed by Team BitFuture
# Website: www.team-bitfuture.de | Email: info@team-bitfuture.de
# Lead Developer: Ossenbrück
# Website: ossenbrück.de | Email: hi@ossenbrück.de

import logging
from datetime import datetime, timedelta
import os
from config import load_config
from data_gatherer import collect_evidence
from data_analyzer import analyze_clues
from report_compiler import compile_case_file

# Set up our investigation log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def investigate_finances() -> bool:
    """
    Our main investigation process to uncover financial insights!

    Returns:
        bool: True if the investigation was successful, False otherwise.
    """
    try:
        # 1. Review the case file (config)
        case_details = load_config('config.yaml')
        logging.info("📂✅ Case file successfully decoded!")

        # Ensure end_date is today if not specified
        if 'end_date' not in case_details or not case_details['end_date']:
            case_details['end_date'] = datetime.now().strftime('%Y-%m-%d')

        # Ensure start_date is one year ago if not specified
        if 'start_date' not in case_details or not case_details['start_date']:
            start_date = datetime.now() - timedelta(days=365)
            case_details['start_date'] = start_date.strftime('%Y-%m-%d')

        # 2. Collect financial evidence (data)
        raw_evidence = collect_evidence(case_details['stocks'], case_details['start_date'], case_details['end_date'])
        logging.info("🔍💼 Financial evidence gathered from the scene!")

        # 3. Analyze our clues (analyze data)
        analyzed_clues = analyze_clues(raw_evidence)
        logging.info("🔬💡 Evidence analyzed, patterns emerging!")

        # 4. Compile our case file (generate report)
        output_files = compile_case_file(analyzed_clues, case_details['report_format'])
        logging.info("📊✅ Case file compiled with all findings!")

        # 5. Verify the output file exists
        if not os.path.exists(output_files['output_file']):
            raise FileNotFoundError(f"Output file not found: {output_files['output_file']}")

        # 6. Clean up temporary files (if any)
        for file in output_files.get('temp_files', []):
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                logging.warning(f"Failed to remove temporary file {file}: {e}")

        logging.info("🧹 Temporary files cleaned up!")

        return True

    except Exception as e:

        logging.error(f"🚨 Investigation hit a snag! Error: {e}")

        return False


if __name__ == "__main__":

    logging.info("🕵️‍♀️🔍 Financial Detective Agency: New case opened!")

    success = investigate_finances()

    if success:
        logging.info("🏆🔍 Case closed successfully. Great work, detective!")
    else:
        logging.info("😔🔍 Case closed unsuccessfully. Better luck next time, detective!")
