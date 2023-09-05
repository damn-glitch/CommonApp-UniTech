import { Button, Heading, withAuthenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import { Storage } from "aws-amplify";
import { useEffect, useState } from "react";
import "./App.css";
import { postData } from "./service/api";

function App({ signOut, user }) {
  console.log(user);
  const [file, setFile] = useState(null);
  const [downloadLink, setLink] = useState(null);
  const [isUploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({ loaded: 0, total: 0 });
  const [list, setList] = useState([]);

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const progressBar = ({ loaded, total }) => {
    return (
      <>
        <progress value={loaded} max={total}>
          {loaded}%
        </progress>
      </>
    );
  };
  const onFileSubmit = async () => {
    if (file !== null) {
      setUploading(true);
      console.log(
        await Storage.put(`${user.username}/${file.name}`, file, {
          progressCallback: (progress) => setProgress(progress),
          contentType: file.type,
          level: "private",
        })
      );
      setUploading(false);
    }
    return false;
  };

  const downloadFile = async (fileName) => {
    if (fileName !== null) {
      setLink(await Storage.get(fileName, { level: "private" }));
    }
  };

  const createApplication = async () => {
    return await postData({
      body: {
        SelectedUniversities: ["A", "B", "C", "D", "E", "F"],
        ApplicantValues: { test: "event", event: "event" },
      },
      endpoint: "/create/application",
    });
  };

  const listUserFiles = async () => {
    setList(await Storage.list("", { level: "private" }));
  };
  useEffect(() => {
    listUserFiles();
    console.log(createApplication());
  }, []);
  return (
    <>
      <Heading level={1}>Hello {user.username}</Heading>
      <Button onClick={signOut}>Sign out</Button>
      <div>
        <input type="file" onChange={onFileChange} />
        <Button onClick={onFileSubmit}>Upload File!</Button>
        {isUploading ? progressBar(progress) : <></>}
      </div>
      <div>
        {downloadLink !== null ? (
          <a href={downloadLink} target="_blank" rel="noopener noreferrer">
            Download Link
          </a>
        ) : (
          <></>
        )}
      </div>
      <div>
        <ul>
          {list.map((item, idx) => (
            <li key={idx}>{item["key"]}</li>
          ))}
        </ul>
      </div>
    </>
  );
}

export default withAuthenticator(App);
