import Analyzer from "./components/Analyzer/Analyzer";
import "bootstrap/dist/css/bootstrap.css";
import "./App.css";
import Navbar from "./components/Navbar";
import SideMenu from "./components/SideMenu";

function App() {
  return (
    <div className="app-container">
      <div className="app-sidemenu">
        <SideMenu />
      </div>
      <div className="app-navbar">
        <Navbar />
      </div>
      <div className="app-content">
        <Analyzer />
      </div>
    </div>
  );
}

export default App;
