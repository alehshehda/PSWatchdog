# PSWatchdog http notification server
Uses smtp to send notifications from post request from watchdog script

### API
| Metoda | Endpoint            | Opis                                  | Parametry          |
|--------|----------------------|---------------------------------------|---------------------|
| POST   | `/api/notify`      | Wysyła mail o parametrach             | `severity`, `logs`    |
### .env
```sh
MAILER_EMAIL="example@gmail.com" # mailer login
MAILER_PASSWORD="exam plee pass" # mailer pass
EMAIL="example2@gmail.com" # reciever of the main (admin)
```
### Development server
```sh
npm i
npm run dev
```