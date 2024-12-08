import csv
import datetime
import os
from abc import ABC, abstractmethod

import flet as ft
from playwright.sync_api import sync_playwright


# Abstract Base Class for Scraper
class IScraper(ABC):
    @abstractmethod
    def scrape_data(self, query: str, location: str, on_update: callable) -> list[dict]:
        pass


# Concrete Scraper Implementation
class PlaywrightScraper(IScraper):
    def scrape_data(self, query: str, location: str, on_update: callable) -> list[dict]:
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(f"https://www.paginebianche.it/ricerca?qs={query}&dv={location}")

            # Reject cookies if present
            self.reject_cookies(page)

            # Scrape the data
            while True:
                self.load_more_results(page)
                results.extend(self.extract_results(page, on_update))
                break

            browser.close()

        return results

    @staticmethod
    def reject_cookies(page) -> None:
        """Reject cookies if the button is visible."""
        try:
            reject_button = page.locator(".ubl-cst__btn--reject")
            if reject_button.is_visible():
                reject_button.click()
        except Exception as e:
            print(f"Errore durante il rifiuto dei cookies: {e}")

    @staticmethod
    def load_more_results(page) -> bool:
        """Click the 'Load More' button if it's visible and return whether it was clicked."""
        try:
            load_more_button = page.locator(".click-load-others")
            if load_more_button.is_visible():
                load_more_button.click()
                return True
        except Exception as e:
            print(f"Errore durante il caricamento di più risultati: {e}")
        return False

    def extract_results(self, page, on_update: callable) -> list[dict]:
        """Extract data from the current page."""
        results = []
        cards = page.locator(".list-element--free")
        for i in range(cards.count()):
            try:
                name = cards.nth(i).locator(".list-element__title").text_content()
                address = cards.nth(i).locator(".list-element__address").text_content()

                phone = self.extract_phone_number(cards.nth(i))

                # Real-time update for the GUI
                on_update(name)

                # Append result to the list
                results.append({"Nome": name, "Telefono": phone, "Indirizzo": address})
            except Exception as e:
                print(f"Errore durante l'elaborazione del risultato {i}: {e}")
        return results

    @staticmethod
    def extract_phone_number(card) -> str:
        """Extract the phone number from a card."""
        phone_btn = card.locator(".phone-numbers__cloak.btn")
        try:
            phone_btn.wait_for(state="visible", timeout=5000)
            phone_btn.click()
            phone_locator = card.locator(".tel")
            phone = phone_locator.first.text_content() if phone_locator.count() > 0 else "N/A"
        except Exception:
            phone = "Non disponibile"
        return phone


# Concrete File Writer Implementation
class CSVFileWriter:
    @staticmethod
    def write_to_file(data: list[dict], file_name: str) -> str:
        # Check if the operating system is Windows
        if os.name == 'nt':  # 'nt' is the identifier for Windows
            desktop_dir = "C:\\Users\\ssaorin\\OneDrive - We Can Consulting S.p.A\\Desktop\\"
        else:
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        # Create a 'csv' folder in the selected directory if it doesn't exist
        output_folder = os.path.join(desktop_dir, "csv")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Construct the full file path
        file_path = os.path.join(output_folder, f"{file_name}.csv")

        # Write data to the CSV file
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Nome", "Telefono", "Indirizzo"])
            for row in data:
                writer.writerow([row["Nome"], row["Telefono"], row["Indirizzo"]])

        return file_path


# GUI Class
class ScraperApp:
    def __init__(self, page: ft.Page, scraper, file_writer):
        self.page = page
        self.scraper = scraper
        self.file_writer = file_writer

        self.query = None
        self.location = None
        self.start_btn = None
        self.snack_bar = ft.SnackBar(content=ft.Text(""))
        self.result_container = None  # Container for dynamic results

    def build(self):
        # Set fixed window size and disable resizing
        self.page.window.width = 500
        self.page.window.height = 300
        self.page.window.resizable = False

        # Input fields and button
        self.query = ft.TextField(label="Ragione Sociale", hint_text="Inserisci la ragione sociale", width=220)
        self.location = ft.TextField(label="Località", hint_text="Inserisci la località", width=220)
        self.start_btn = ft.ElevatedButton(text="Inizia Scraping", on_click=self.start_scraping, width=200)

        # Feedback list container
        self.result_container = ft.Column([], visible=False, spacing=10)

        # Add SnackBar to the overlay list
        self.page.overlay.append(self.snack_bar)

        # Page layout
        self.page.add(
            ft.Column(
                [
                    ft.Row([self.query, self.location], alignment="center", spacing=10),
                    ft.Row([self.start_btn], alignment="center"),
                    self.result_container,  # Placeholder for results
                ],
                spacing=15,
                alignment="center",
                expand=True,
            )
        )

    def update_snack_bar(self, message):
        self.snack_bar.content.value = message
        self.snack_bar.open = True
        self.snack_bar.update()

    def start_scraping(self, _):
        query = self.query.value
        location = self.location.value

        if not query:
            self.update_snack_bar("Ragione Sociale non può essere vuota!")
            return

        if not location:
            self.update_snack_bar("Località non può essere vuota!")
            return

        self.start_btn.disabled = True
        self.page.update()

        self.start_btn.text = "Scraping in corso..."
        self.page.update()

        def on_update(name):
            # Real-time update to show each new title as it's found
            self.update_snack_bar(f"Trovato: {name}")

        try:
            # Scrape data
            data = self.scraper.scrape_data(query, location, on_update)
            if not data:
                raise Exception("Nessun dato trovato durante lo scraping!")

            # Save data to a file
            file_name = f"{query}_{location}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_path = self.file_writer.write_to_file(data, file_name)

            self.update_snack_bar(f"Scraping completato! File salvato in: {file_path}")
        except Exception as ex:
            self.update_snack_bar(f"Errore: {str(ex)}")
        finally:
            self.location.value = ""
            self.query.value = ""
            self.start_btn.text = "Inizia Scraping"
            self.start_btn.disabled = False
            self.page.update()


# Main Flet App
def main(page: ft.Page):
    scraper = PlaywrightScraper()
    file_writer = CSVFileWriter()
    app = ScraperApp(page, scraper, file_writer)
    app.build()


if __name__ == "__main__":
    ft.app(target=main)
