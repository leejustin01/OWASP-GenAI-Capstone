/*
 * Spinner derived from https://tobiasahlin.com/spinkit/.
 */

import './Spinner.css'

export default function Spinner() {
    return (
        <div className="spinner">
            <div className="dot" />
            <div className="dot" />
            <div className="dot" />
        </div>
    )
}
