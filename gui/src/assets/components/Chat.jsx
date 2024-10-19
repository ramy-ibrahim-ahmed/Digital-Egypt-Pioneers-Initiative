import React, { useContext } from "react";
import fcaih from "../img/facih.png";
import me from "../img/me2.jpg";
import { BotContext } from "../context/context";
import { DNA ,Bars} from "react-loader-spinner";
import { Input } from "postcss";

export default function Chat() {
  const {
    onSent,
    showResult,
    loading,
    resultData,
    setInPut,
    inPut,
    recPrompets,
    setRecPrompts,
  } = useContext(BotContext);
  return (
    <>
      <div className="chat-page  h-screen  w-screen  bg-[#131314] ">
        <div className="container m-auto h-[100%] relative">
          <nav className="flex w-[90%] md:w-3/4 justify-between h-fit py-3 px-1 m-auto">
            <div className="logo flex items-center gap-2">
              <div className="text bg-gradient-to-r from-[#6d7ce0] via-[#a470bd] to-[#c3698f] bg-clip-text">
                <h1 className="text-xl font-bold text-transparent">
                  FCAIH Bot
                </h1>
              </div>
            </div>
            <div className="user_name flex gap-2 items-center">
              {/* <div className="img w-7 ">
                        <img src={me} alt="" className='w-7 rounded-full h-7 ' />
                    </div>
                    <div className="text bg-gradient-to-r from-[#6d7ce0] via-[#a470bd] to-[#c3698f] bg-clip-text">
                        <h3 className='text-l font-bold text-transparent'>Mazen Ahmed </h3>
                    </div> */}
            </div>
          </nav>
          {showResult ? (
            <div className="result  w-[85%] md:w-[40%] m-auto h-[75%] overflow-auto">
              <div className="result-title flex gap-4 ms-1 items-center">
                <i className="fa-solid fa-user text-[#6d7ce0]"></i>
                <p className="text-white">{recPrompets}</p>
              </div>
              <div className="responce mt-4 flex gap-2">
                <img
                  src={fcaih}
                  alt=""
                  className="w-7 rounded-full h-7 w-6 h-6 "
                />
                {!loading?<p className='text-white' dangerouslySetInnerHTML={{__html:resultData}}></p>
                :<div className="load w-full h-48 bg-purple-500 flex justify-center items-center rounded-xl bg-[rgba(223,223,223,0.16)] ">
                  <Bars
                    height="100"
                    width="200"  
                    color="#6d7ce0"
                    ariaLabel="bars-loading"
                    wrapperStyle={{}}
                    wrapperClass=""
                    visible={true}
                  />
                  
                </div>}
              </div>
            </div>
          ) : (
            <>
              <div className="result  w-[85%] md:w-[40%] m-auto h-[75%] overflow-auto">
                <div className="logo ">
                  <div className="flex items-center gap-3 text bg-gradient-to-r from-[#6d7ce0] via-[#a470bd] to-[#c3698f] bg-clip-text">
                    <i className="fa-brands fa-bots text-transparent text-4xl "></i>
                    <h1 className="text-xl font-bold text-transparent">
                      Hello This is Our College Assistant Bot
                    </h1>
                  </div>
                  <h1 className="text-xl font-bold text-white">
                    It Can assist You By Answering any Question About Our
                    College!!
                  </h1>
                </div>
                <div className="img w-1/2  m-auto  flex justify-center items-center mt-5">
                  <img src={fcaih} alt="" />
                </div>
              </div>
            </>
          )}

          <div className="main  md:w-4/5 m-auto absolute bottom-6 right-0 left-0 ">
            <div className="prompt m-auto  w-[90%] md:w-2/3 relative ">
              <input
                onChange={(e) => {
                  setInPut(e.target.value);
                }}
                value={inPut}
                placeholder="Enter Prompt Here"
                className="w-full py-3 rounded-3xl px-5 bg-[#1e1f20] text-white"
                type="search"
              />
              <button
                onClick={() => {
                  onSent();
                }}
                className="absolute right-6 top-3"
              >
                <i className="fa-solid fa-share text-lg text-white"></i>
              </button>
            </div>
            <p className="text-white text-[15px] text-center mt-2">
              Gemini may display inaccurate info, including about people
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
