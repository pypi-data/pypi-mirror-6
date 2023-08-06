// This file is part of the python-chess library.
// Copyright (C) 2013 Niklas Fiekas <niklas.fiekas@tu-clausthal.de>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have recieved a copy of the GNU General Public License
// along with this program. If not, see <http://gnu.org/licenses/>.

#include "move.h"

#include <boost/format.hpp>

namespace chess {

Move::Move(const Square& source, const Square& target, char promotion) : m_source(source), m_target(target) {
    if (!source.is_valid()) {
        throw std::invalid_argument("source");
    }

    if (!target.is_valid()) {
        throw std::invalid_argument("target");
    }

    switch (promotion) {
        case 'r':
        case 'n':
        case 'b':
        case 'q':
            m_promotion = promotion;
            break;
        default:
            throw std::invalid_argument("promotion");
    }
}

Move::Move(const Square& source, const Square& target) : m_source(source), m_target(target) {
    if (!source.is_valid()) {
        throw std::invalid_argument("source");
    }

    if (!target.is_valid()) {
        throw std::invalid_argument("target");
    }


    m_promotion = 0;
}

Move::Move(const std::string& uci) : m_source(Square(0)), m_target(Square(0)) {
    if (uci.length() == 4 || uci.length() == 5) {
        m_source = Square(uci.substr(0, 2));
        m_target = Square(uci.substr(2, 2));
        if (uci.length() == 5) {
            m_promotion = uci.at(4);
            switch (m_promotion) {
                case 'r':
                case 'n':
                case 'b':
                case 'q':
                    break;
                default:
                    throw std::invalid_argument("uci");
            }
        } else {
            m_promotion = 0;
        }
    }
    else {
        throw new std::invalid_argument("uci");
    }
}

Move::Move(const Move& move) {
    m_source = move.m_source;
    m_target = move.m_target;
    m_promotion = move.m_promotion;
}

Square Move::source() const {
    return m_source;
}

Square Move::target() const {
    return m_target;
}

char Move::promotion() const {
    return m_promotion;
}

std::string Move::full_promotion() const {
    switch (m_promotion) {
        case 'r':
            return "rook";
        case 'b':
            return "bishop";
        case 'n':
            return "knight";
        case 'q':
            return "queen";
    }

    throw std::logic_error("Unknown promotion type.");
}

std::string Move::uci() const {
    if (m_promotion) {
        return m_source.name() + m_target.name() + m_promotion;
    } else {
        return m_source.name() + m_target.name();
    }
}

bool Move::is_promotion() const {
    return m_promotion != 0;
}

std::string Move::__repr__() const {
    return boost::str(boost::format("Move.from_uci('%s')") % uci());
}

int Move::__hash__() const {
    return m_source.__hash__() + 100 * m_target.__hash__() + 10000 * m_promotion;
}

Move& Move::operator=(const Move& rhs) {
    m_source = rhs.m_source;
    m_target = rhs.m_target;
    m_promotion = rhs.m_promotion;
    return *this;
}

bool Move::operator==(const Move& rhs) const {
    return m_source == rhs.m_source && m_target == rhs.m_target && m_promotion == rhs.m_promotion;
}

bool Move::operator!=(const Move& rhs) const {
    return m_source != rhs.m_source || m_target != rhs.m_target || m_promotion != rhs.m_promotion;
}

Move Move::from_uci(const std::string& uci) {
    return Move(uci);
}

std::ostream& operator<<(std::ostream& out, const Move& move) {
    out << move.uci();
    return out;
}

} // namespace chess
