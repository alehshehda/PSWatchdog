import express, { Request, Response } from "express";
import cors from "cors";
import path from "path";
import dotenv from "dotenv";
import bodyParser from "body-parser";
import nodemailer from "nodemailer";
dotenv.config();
const app = express();
app.use(express.json());
app.use(cors());
app.use(bodyParser.json());

const transporter = nodemailer.createTransport({
  port: 465, 
  host: "smtp.gmail.com",
  auth: {
    user: process.env.MAILER_EMAIL,
    pass: process.env.MAILER_PASSWORD,
  },
  secure: true,
});
const unknownEndpoint = (_req: Request, res: Response) => {
  res.status(404).send({ error: "unknown endpoint" });
};

app.get("/", (_req: Request, res: Response) => {
  res.json({ message: "Welcome to PSWatchdog API" });
});
app.get("/api/email", (_req: Request, res: Response) => {
  res.send({ email: process.env.EMAIL });
});

app.post("/api/notify", (req: Request, res: Response) => {
  const { logs, severity } = req.body;
  const mailData = {
    from: process.env.MAILER_EMAIL, // sender address
    to: process.env.EMAIL,
    subject: `PSWatchdog - ${severity}`, // Subject line
    // embed HTML logs in the email body
    html: `<h1>PSWatchdog - ${severity ?? null}</h1><p>${logs}</p>`,
  };
  transporter.sendMail(mailData, function (err, _info) {
    if (err) res.send({ message: "Error", error: err });
    else res.send({ message: "Success" });
  });
});

app.use(unknownEndpoint);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
