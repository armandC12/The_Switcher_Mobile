import { useGameContext } from '../../context/GameContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { calculateFigures, leaveGame } from "@/services/services";
import { MdLogout } from "react-icons/md";


export default function LeaveButton({ gameId, setLoadingOut }) {
  const { playerId } = useGameContext();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [showTooltip, setShowTooltip] = useState(false);
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    setTimeout(() => setShowError(false), [1000])
  }, [showError, setShowError])

  const onAbandon = async () => {
    
      leaveGame(playerId, gameId).then((res) => {
        // console.log(res)
        if (res.reverted_movements) {
          setLoadingOut(true);
          return calculateFigures(gameId);
        }
        navigate('/games');
      }).catch(error => {
        setError(error.message);
        setShowError(true);
        console.error(error);
      }). finally(() => {
        setLoadingOut(false);
        navigate('/games');
      })

  }

  return (
    <div className="relative"> 
      <button
        data-testid='leaveButtonId'
        onClick={onAbandon}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="text-white hover:scale-110 transition-transform"

      >
        <MdLogout size={40} />
      </button>

      {showTooltip && (
        <div className="absolute bottom-full w-fit mb-2 z-50 p-2 text-sm bg-gray-700 text-white rounded">
            Abandonar
        </div>
      )}

      {showError && (
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-600 text-white p-4 rounded shadow-md z-50">
              {error}
          </div>
      )}
    </div>
  );
}
