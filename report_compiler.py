import matplotlib.pyplot as plt
from fpdf import FPDF
import logging
import os
from PyPDF2 import PdfMerger
from typing import Dict, Any, List


def compile_case_file(analyzed_clues: Dict[str, Dict[str, Any]], report_format: str) -> Dict[str, Any]:
    """
    Compile all analyzed clues into a comprehensive case file (report).

    Args:
        analyzed_clues (Dict[str, Dict[str, Any]]): Dictionary containing analyzed financial data.
        report_format (str): Format of the report ('pdf' or 'txt').

    Returns:
        Dict[str, Any]: Dictionary containing output file information and temporary files.

    Raises:
        ValueError: If an unsupported report format is provided.
    """
    logging.info(f"📊 Compiling case file in {report_format} format...")

    if report_format == 'pdf':
        return _generate_pdf_report(analyzed_clues)
    elif report_format == 'txt':
        return _generate_txt_report(analyzed_clues)
    else:
        logging.error(f"🚫 Unsupported report format: {report_format}")
        raise ValueError(f"Unsupported report format: {report_format}")


def _generate_pdf_report(analyzed_clues: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a PDF report with charts and key statistics.

    Args:
        analyzed_clues (Dict[str, Dict[str, Any]]): Dictionary containing analyzed financial data.

    Returns:
        Dict[str, Any]: Dictionary containing the path to the merged PDF and list of temporary files.
    """
    pdf_files = []
    temp_files = []

    for stock, data in analyzed_clues.items():
        pdf = FPDF()
        pdf.add_page()

        # 📝 Header
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(200, 10, txt=f"Detective's Report: {stock}", ln=1, align='C')
        pdf.ln(5)

        # 🔍 Key Statistics Section
        _add_key_statistics_section(pdf, data)

        # 📈 Momentum Indicators Section
        _add_momentum_indicators_section(pdf, data)

        # 📊 Charts
        _add_charts_to_pdf(pdf, stock, data, temp_files)

        # 💾 Save individual stock report
        pdf_file = f"financial_case_file_{stock}.pdf"
        pdf.output(pdf_file)
        pdf_files.append(pdf_file)
        logging.info(f"📄 PDF case file for {stock} compiled successfully!")

    # 🔗 Merge all PDF files
    merged_pdf = "financial_case_file_complete.pdf"
    _merge_pdf_files(pdf_files, merged_pdf)

    # 🧹 Clean up temporary files
    _cleanup_temp_files(pdf_files + temp_files)

    return {"output_file": merged_pdf, "temp_files": []}


def _add_key_statistics_section(pdf: FPDF, data: Dict[str, Any]):
    """
    Add the Key Statistics section to the PDF report with left alignment.

    Args:
        pdf (FPDF): The PDF object to add content to.
        data (Dict[str, Any]): Dictionary containing the financial data for a stock.
    """
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(200, 10, txt="Key Intel:", ln=1)
    pdf.set_font("helvetica", "", 10)

    # Layout parameters
    col_widths = [30, 70, 30, 70]
    row_height = 8

    # Row 1: Price and Volatility
    pdf.cell(col_widths[0], row_height, txt="Price:")
    pdf.cell(col_widths[1], row_height, txt=f"${data['latest_price']:.2f}")
    _add_linked_cell(pdf, "Volatility:", "https://www.investopedia.com/terms/v/volatility.asp", col_widths[2])
    pdf.cell(col_widths[3], row_height, txt=f"{data['volatility']:.4f}", ln=1)

    # Row 2: Sharpe Ratio and ATR
    _add_linked_cell(pdf, "Sharpe Ratio:", "https://www.investopedia.com/terms/s/sharperatio.asp", col_widths[0])
    pdf.cell(col_widths[1], row_height, txt=f"{data['sharpe_ratio']:.4f}")
    _add_linked_cell(pdf, "ATR:", "https://www.investopedia.com/terms/a/atr.asp", col_widths[2])
    pdf.cell(col_widths[3], row_height, txt=f"{data['atr']:.4f}", ln=1)

    # Row 3: ROC (Average and Latest)
    _add_linked_cell(pdf, "Avg ROC:", "https://www.investopedia.com/terms/p/pricerateofchange.asp", col_widths[0])
    pdf.cell(col_widths[1], row_height, txt=f"{data['avg_roc']:.2f}%")
    pdf.cell(col_widths[2], row_height, txt="Latest ROC:")
    pdf.cell(col_widths[3], row_height, txt=f"{data['latest_roc']:.2f}%", ln=1)

    pdf.ln(3)


def _add_momentum_indicators_section(pdf: FPDF, data: Dict[str, Any]):
    """
    Add the Momentum Indicators section to the PDF report with left alignment.

    Args:
        pdf (FPDF): The PDF object to add content to.
        data (Dict[str, Any]): Dictionary containing the financial data for a stock.
    """
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(200, 10, txt="Momentum Signals:", ln=1)
    pdf.set_font("helvetica", "", 10)

    # Layout parameters
    col_widths = [30, 70, 50, 50]
    row_height = 8

    # Row 1: RSI and MACD
    _add_linked_cell(pdf, "RSI:", "https://www.investopedia.com/terms/r/rsi.asp", col_widths[0])
    pdf.cell(col_widths[1], row_height, txt=f"{data['rsi']:.2f}")
    _add_linked_cell(pdf, "MACD:", "https://www.investopedia.com/terms/m/macd.asp", col_widths[2])
    pdf.cell(col_widths[3], row_height, txt=f"{data['macd']:.4f}", ln=1)

    # Row 2: MACD Signal and Bollinger Bands
    pdf.cell(col_widths[0], row_height, txt="MACD Signal:")
    pdf.cell(col_widths[1], row_height, txt=f"{data['macd_signal']:.4f}")
    _add_linked_cell(pdf, "Bollinger Bands", "https://www.investopedia.com/terms/b/bollingerbands.asp", col_widths[2])
    pdf.cell(col_widths[3], row_height, txt=f"Avg Gap: ${data['avg_bb_gap']:.2f}", ln=1)

    pdf.ln(3)


def _add_linked_cell(pdf: FPDF, text: str, url: str, width: int):
    """
    Add a cell with blue, underlined, hyperlinked text to the PDF.

    Args:
        pdf (FPDF): The PDF object to add content to.
        text (str): The text to display and link.
        url (str): The URL to link to.
        width (int): The width of the cell.
    """
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("", "U")
    pdf.cell(width, 8, txt=text, link=url)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("", "")


def _add_charts_to_pdf(pdf: FPDF, stock: str, data: Dict[str, Any], temp_files: List[str]):
    """
    Generate and add charts to the PDF report, ensuring all content fits on one page.

    Args:
        pdf (FPDF): The PDF object to add content to.
        stock (str): The stock symbol.
        data (Dict[str, Any]): Dictionary containing the financial data for the stock.
        temp_files (List[str]): List to append temporary file names for later cleanup.
    """
    try:
        # 📈 Generate and save price chart with Bollinger Bands and RSI
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
        ax1.plot(data['price_data']['Close'], label='Close Price')
        ax1.plot(data['price_data']['UpperBand'], label='Upper BB', linestyle='--')
        ax1.plot(data['price_data']['LowerBand'], label='Lower BB', linestyle='--')
        ax1.set_title(f"{stock} Price with Bollinger Bands")
        ax1.set_ylabel("Price")
        ax1.legend(loc='upper left', fontsize='xx-small')

        ax2.plot(data['price_data']['RSI'], label='RSI', color='purple')
        ax2.axhline(y=70, color='r', linestyle='--', linewidth=0.5)
        ax2.axhline(y=30, color='g', linestyle='--', linewidth=0.5)
        ax2.set_ylabel("RSI")
        ax2.set_ylim(0, 100)
        ax2.legend(loc='upper left', fontsize='xx-small')

        plt.xlabel("Date")
        plt.tight_layout()
        plt.savefig(f"{stock}_price_bb_rsi_chart.png", dpi=300, bbox_inches='tight')
        plt.close()

        pdf.image(f"{stock}_price_bb_rsi_chart.png", x=10, y=None, w=190)
        temp_files.append(f"{stock}_price_bb_rsi_chart.png")

        # Add a small space between charts
        pdf.ln(3)

        # 📊 Generate and save MACD chart
        plt.figure(figsize=(10, 2.5))
        plt.plot(data['macd_data']['MACD'], label='MACD')
        plt.plot(data['macd_data']['Signal'], label='Signal')
        plt.bar(data['macd_data'].index, data['macd_data']['MACD'] - data['macd_data']['Signal'], label='Histogram')
        plt.title(f"{stock} MACD")
        plt.xlabel("Date")
        plt.ylabel("MACD")
        plt.legend(loc='upper left', fontsize='xx-small')
        plt.tight_layout()
        plt.savefig(f"{stock}_macd_chart.png", dpi=300, bbox_inches='tight')
        plt.close()

        pdf.image(f"{stock}_macd_chart.png", x=10, y=None, w=190)
        temp_files.append(f"{stock}_macd_chart.png")

    except Exception as e:
        logging.error(f"❌ Error generating charts for {stock}: {e}")
        pdf.cell(200, 10, txt=f"Error generating charts: {e}", ln=1)


def _merge_pdf_files(pdf_files: List[str], output_file: str):
    """
    Merge multiple PDF files into a single file.

    Args:
        pdf_files (List[str]): List of PDF file paths to merge.
        output_file (str): Path for the merged output PDF file.
    """
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()

    # ✅ Verify that the merged PDF was created successfully
    if not os.path.exists(output_file):
        logging.error(f"❌ Failed to create merged PDF: {output_file}")
        raise FileNotFoundError(f"Merged PDF not found: {output_file}")

    logging.info("✅ All PDF case files compiled and merged successfully!")


def _cleanup_temp_files(temp_files: List[str]):
    """
    Clean up temporary files created during report generation.

    Args:
        temp_files (List[str]): List of temporary file paths to delete.
    """
    for file in temp_files:
        try:
            os.remove(file)
        except Exception as e:
            logging.warning(f"⚠️ Failed to remove temporary file {file}: {e}")


def _generate_txt_report(analyzed_clues: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a simple text report with key statistics.

    Args:
        analyzed_clues (Dict[str, Dict[str, Any]]): Dictionary containing analyzed financial data.

    Returns:
        Dict[str, Any]: Dictionary containing the path to the output text file.
    """
    output_file = "financial_case_file.txt"
    with open(output_file, "w") as file:
        file.write("Financial Detective Agency: Case File\n\n")

        for stock, data in analyzed_clues.items():
            file.write(f"Stock: {stock}\n")
            file.write(f"Latest Price: ${data['latest_price']:.2f}\n")
            file.write(f"Volatility: {data['volatility']:.4f} (https://www.investopedia.com/terms/v/volatility.asp)\n")
            file.write(f"Sharpe Ratio: {data['sharpe_ratio']:.4f} (https://www.investopedia.com/terms/s/sharperatio.asp)\n")
            file.write(f"Average True Range (ATR): {data['atr']:.4f} (https://www.investopedia.com/terms/a/atr.asp)\n")
            file.write(f"Average Rate of Change (ROC): {data['avg_roc']:.2f}% (https://www.investopedia.com/terms/p/pricerateofchange.asp)\n")
            file.write(f"Latest Rate of Change (ROC): {data['latest_roc']:.2f}%\n")
            file.write(f"RSI: {data['rsi']:.2f} (https://www.investopedia.com/terms/r/rsi.asp)\n")
            file.write(f"MACD: {data['macd']:.4f} (https://www.investopedia.com/terms/m/macd.asp)\n")
            file.write(f"MACD Signal: {data['macd_signal']:.4f}\n")
            file.write(f"Average Bollinger Bands Gap: ${data['avg_bb_gap']:.2f} (https://www.investopedia.com/terms/b/bollingerbands.asp)\n\n")

    logging.info("✅ Text case file compiled successfully!")

    return {"output_file": output_file, "temp_files": []}
