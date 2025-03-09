import { useGameContext } from "@/context/GameContext";
import { useSocketContext } from "@/context/SocketContext";
import { calculateFigures } from "@/services/services";
import {useEffect} from "react";

export function useUpdateBoardSocket(activeGameId, fetchBoard, setSyncEffect, setLoadingFig) {
    const {socket} = useSocketContext();
    const { currentTurn, playerId } = useGameContext();

    useEffect(() => {
        if (!socket || !activeGameId || !fetchBoard) return;

        const handleUptadeBoard = async (event) => {
            const data = JSON.parse(event.data);

            if (data.type === `${activeGameId}:MOVEMENT_UPDATE`) {
                console.log("FETCHING BOARD MOV")
                fetchBoard().then((res) => {

                    if (currentTurn===playerId) {
                        setSyncEffect(false);
                        setLoadingFig(true);
                        calculateFigures(activeGameId).then((res) => {
                            setSyncEffect(true)
                            setLoadingFig(false);
                        })
                    }
                })

            }
            if (((data.type === `${activeGameId}:BOARD_UPDATE`) && (currentTurn === playerId))) {
                console.log("FETCHING BOARD FIG CALC")
                console.log(`current Turn board update: ${currentTurn}`)
                fetchBoard().then((res) => {
                    setLoadingFig(false);
                    setSyncEffect(true);
                })
            }

        }
        socket.addEventListener("message", handleUptadeBoard);
        return () => {
            socket.removeEventListener("message", handleUptadeBoard);
        };
    }, [socket, activeGameId, fetchBoard, playerId, currentTurn])
}