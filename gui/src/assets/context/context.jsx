import { createContext, useState } from "react";
import React from 'react'
import axios from "axios";
import run from "../js/gemini";



export const BotContext = createContext()


export default function ContextProvider({ children }) {
    const [inPut, setInPut] = useState("")
    const [recPrompets, setRecPrompts] = useState("")
    const [PrevPrompets, setPrevPrompts] = useState("")
    const [showResult, setShowResult] = useState(false)
    const [loading, setLoading] = useState(false)
    const [resultData, setResultData] = useState("")
    const delay = (i, next) => {
        setTimeout(function () {
            setResultData(prev => prev + next)
        }, 75 * i)
    }
    async function onSent(prompt) {
        setResultData("")
        setLoading(true)
        setShowResult(true)
        setRecPrompts(inPut)
        setInPut("")



        let response;
        axios.post("http://127.0.0.1:8000/chat", {
            "query": inPut
        }).then(({ data }) => {
            response = data.response
            console.log(response)
        })





        // let resarray = response.split("**")
        // let newRes;
        // for (let i = 0; i < resarray.length; i++) {
        //     if (i === 0 || i % 2 !== 1) {
        //         newRes += resarray[i]
        //     } else {
        //         newRes += "<b>" + resarray[i] + "</b>"
        //     }
        // }
        // let fres = newRes.split("*").join("</br>")
        // let arrnew = fres.split(" ")
        // for (let i = 0; i < arrnew.length; i++) {
        //     const nextt = arrnew[i]
        //     delay(i, nextt + " ")
        // }
        //    setResultData(fres)
        setLoading(false)

    }
    const value = {
        onSent,
        inPut,
        setInPut,
        PrevPrompets,
        setPrevPrompts,
        showResult,
        setShowResult,
        showResult,
        setShowResult,
        loading,
        setLoading,
        resultData,
        setResultData,
        recPrompets,
        setRecPrompts
    }
    return (
        <BotContext.Provider value={value}>
            {children}
        </BotContext.Provider>


    )
}
