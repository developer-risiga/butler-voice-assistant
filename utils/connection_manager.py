import time
import logging
import requests
from openai import OpenAI
from config.settings import CONFIG

class ConnectionManager:
    def __init__(self):
        self.max_retries = CONFIG["max_retries"]
        self.timeout = CONFIG["timeout"]
        self.service_status = {}
        
    def check_services_health(self):
        logging.info("Checking service health...")
        
        services_to_check = {
            "openai": self._check_openai_health,
            "internet": self._check_internet_connection,
        }
        
        all_healthy = True
        for service, check_func in services_to_check.items():
            try:
                status, message = check_func()
                self.service_status[service] = {"status": status, "message": message}
                
                if status == "healthy":
                    logging.info(f"  {service}: {message}")
                else:
                    logging.warning(f"  {service}: {message}")
                    all_healthy = False
                    
            except Exception as e:
                self.service_status[service] = {"status": "error", "message": str(e)}
                logging.error(f"  {service}: Health check failed - {e}")
                all_healthy = False
        
        return all_healthy
    
    def _check_openai_health(self):
        try:
            client = OpenAI(api_key=CONFIG["openai_api_key"])
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=5,
                timeout=5
            )
            
            if response.choices[0].message.content:
                return "healthy", "API responsive"
            else:
                return "unhealthy", "Empty response"
                
        except Exception as e:
            return "unhealthy", f"API error: {str(e)}"
    
    def _check_internet_connection(self):
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                return "healthy", "Connected"
            else:
                return "unhealthy", f"HTTP {response.status_code}"
        except Exception as e:
            return "unhealthy", f"No connection: {str(e)}"
    
    def with_retry(self, func, *args, **kwargs):
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                logging.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = 1 * (2 ** attempt)
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        logging.error(f"All {self.max_retries} retries failed for {func.__name__}")
        raise last_exception

connection_manager = ConnectionManager()
