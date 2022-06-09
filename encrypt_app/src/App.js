import React, { useRef, useState } from "react";
import "./App.css";
import StringCrypto from "string-crypto";
import firebase from "firebase/app";
import "firebase/firestore";
import "firebase/auth";
import "firebase/analytics";
import { useAuthState } from "react-firebase-hooks/auth";
import { useCollectionData } from "react-firebase-hooks/firestore";
import {hashed_key} from "./components/keycheck"
import sha256 from "sha256"
firebase.initializeApp({
  apiKey: "AIzaSyABEPMeLah3wCOyKa38gz-oxByUzZllTEg",
  authDomain: "chat-encrypt.firebaseapp.com",
  projectId: "chat-encrypt",
  storageBucket: "chat-encrypt.appspot.com",
  messagingSenderId: "813966482173",
  appId: "1:813966482173:web:87b975e973257ea95b7c94",
  measurementId: "G-ZZEVPRYJJK",
});
const auth = firebase.auth();
const firestore = firebase.firestore();
const analytics = firebase.analytics();

function App() {
  
  const [user] = useAuthState(auth);

  return (
    <div className="App">
      <header>
        <h1>💬 Do You Have The key?</h1>
        <SignOut />
      </header>

      <section>{user ? <ChatRoom /> : <SignIn />}</section>
    </div>
  );
}

function SignIn() {
  const signInWithGoogle = () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider);
  };

  return (
    <>
      <button className="sign-in" onClick={signInWithGoogle}>
        Sign in with Google
      </button>
      <p className="sign-in-text">
        Welcome to our encrypted chat app please sign in .
      </p>
    </>
  );
}

function SignOut() {
  return (
    auth.currentUser && (
      <button className="sign-out" onClick={() => auth.signOut()}>
        Sign Out
      </button>
    )
  );
}

function ChatRoom() {
  const [KEYY, setKEYY] = useState('');
  const [locked, setLocked] = useState(true);
  const [type, setType] = useState("file");
  const [style, setStyle] = useState({ display: "none" });

  const [placeholder, setPlaceholder] = useState("enter todays key");
  const dummy = useRef();
  const messagesRef = firestore.collection("messages");
  const query = messagesRef.orderBy("createdAt").limit(100);

  const [messages] = useCollectionData(query, { idField: "id" });

  const [formValue, setFormValue] = useState("");

  const sendMessage = async (e) => {
    e.preventDefault();

    const { uid, photoURL } = auth.currentUser;
    const { encryptString, decryptString } = new StringCrypto();
    console.log("sendingwith this key "+KEYY)
    let encryptedString = encryptString(formValue, KEYY);
    await messagesRef.add({
      text: encryptedString,
      createdAt: firebase.firestore.FieldValue.serverTimestamp(),
      uid,
      photoURL,
    });

    setFormValue("");
    dummy.current.scrollIntoView({ behavior: "smooth" });
  };
  function EnterKey(e) {
    e.preventDefault();
    if ((sha256(formValue) == hashed_key)&& (locked)) {
      setLocked(false);
      setKEYY(formValue);
      console.log(KEYY + " changed key")
      setPlaceholder("Write your message");
    }
    setFormValue("");
  }


 

  return (
    <>
      <main>
        {messages &&
          messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} locked={locked} KEY={KEYY} />
          ))}

        <span ref={dummy}></span>
      </main>
      <div>
        <form onSubmit={sendMessage}>
          
            <input
              value={formValue}
              onChange={(e) => setFormValue(e.target.value)}
              placeholder={placeholder}
            />
         

          {locked ? (
            <button onClick={EnterKey}>🔒</button>
          ) : (
            <button type="submit" disabled={!formValue}>
              🕊️
            </button>
          )}
        </form>
      </div>
    </>
  );
}

function ChatMessage(props) {
  const { text, uid, photoURL } = props.message;
  const KEY=props.KEY
  console.log("inside chatmessage"+KEY)

  const messageClass = uid === auth.currentUser.uid ? "sent" : "received";
  const { encryptString, decryptString } = new StringCrypto();
  return (
    <>
      <div className={`message ${messageClass}`}>
        <img
          src={
            photoURL || "https://api.adorable.io/avatars/23/abott@adorable.png"
          }
        />
        {props.locked ? (
          <p>{text}</p>
        ) : (
          <p>{decryptString(text, KEY)}</p>
        )}
      </div>
    </>
  );
}

export default App;
